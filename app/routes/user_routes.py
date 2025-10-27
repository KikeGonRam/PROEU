from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.user import (
    UserCreate, UserUpdate, UserResponse, UserLogin, 
    Token, UserListResponse, UserRole, UserStatus
)
from app.controllers.user_controller import user_controller
from app.middleware.auth_middleware import get_optional_current_user

# Configurar router
router = APIRouter()

# Configurar seguridad
security = HTTPBearer()

# Dependency para obtener usuario actual
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserResponse:
    """Obtener usuario actual desde el token"""
    email = user_controller.verify_token(credentials.credentials)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await user_controller.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return UserResponse(**user.dict())

# Dependency para verificar si es admin
async def get_current_admin_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Verificar que el usuario actual es administrador"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador"
        )
    return current_user

# Rutas de autenticación
@router.post("/login", response_model=Token, summary="Iniciar sesión")
async def login(login_data: UserLogin, response: Response, request: Request):
    """
    Iniciar sesión con email y contraseña.
    Retorna un token JWT para autenticación.
    """
    token = await user_controller.login(login_data)
    # Debug: log incoming request headers and cookies to help diagnose cookie issues
    try:
        print(f"[DEBUG] /api/users/login request.headers: {dict(request.headers)}")
        print(f"[DEBUG] /api/users/login request.cookies: {request.cookies}")
    except Exception:
        pass
    # Set a secure HttpOnly cookie so server-rendered pages can also
    # detect the logged-in user on subsequent navigations.
    # Cookie value is the raw access token (jwt). Keep it HttpOnly to
    # avoid XSS access; client JS will continue to use localStorage.
    try:
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,
            samesite="lax",
            # secure=False so it works in local dev (http); in prod set True
            secure=False,
            max_age=60 * 60 * 24 * 7  # 7 days
        )
        try:
            print(f"[DEBUG] set_cookie called for access_token (len={len(token.access_token)})")
        except Exception:
            pass
    except Exception:
        # If setting cookie fails for some environment, still return token.
        pass

    return token

@router.post("/register", response_model=UserResponse, summary="Registro público")
async def register(user_data: UserCreate):
    """
    Registro público de nuevos usuarios.
    Los usuarios registrados públicamente tienen rol 'solicitante' por defecto.
    """
    # Forzar rol de solicitante para registros públicos
    user_data.role = UserRole.SOLICITANTE
    user_data.status = UserStatus.ACTIVE
    
    return await user_controller.create_user(user_data)

@router.get("/me", response_model=UserResponse, summary="Obtener perfil actual")
async def get_current_user_profile(current_user: UserResponse = Depends(get_current_user)):
    """
    Obtener el perfil del usuario autenticado.
    """
    return current_user

@router.post("/refresh", response_model=Token, summary="Renovar token")
async def refresh_token(current_user: UserResponse = Depends(get_current_user)):
    """
    Renovar el token JWT del usuario autenticado.
    """
    return await user_controller.refresh_token(current_user.email)


@router.post('/logout', summary="Logout y borrar cookie")
async def logout(response: Response, current_user: UserResponse | None = Depends(get_optional_current_user)):
    """
    Endpoint para cerrar sesión: borra la cookie `access_token`.
    Se permite ser llamado aunque no haya usuario autenticado (idempotente).
    """
    # Borrar cookie (será silencioso si no existe)
    try:
        response.delete_cookie('access_token', path='/')
    except Exception:
        pass
    return {"message": "Sesión cerrada"}

# Rutas CRUD (solo para administradores)
@router.post("/", response_model=UserResponse, summary="Crear usuario")
async def create_user(
    user_data: UserCreate,
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Crear un nuevo usuario.
    Solo los administradores pueden crear usuarios.
    """
    return await user_controller.create_user(user_data)

@router.get("/", response_model=UserListResponse, summary="Listar usuarios")
async def get_users(
    page: int = Query(1, ge=1, description="Número de página"),
    limit: int = Query(5, ge=1, le=100, description="Elementos por página"),
    search: Optional[str] = Query(None, description="Buscar por nombre, apellido, email o departamento"),
    role: Optional[UserRole] = Query(None, description="Filtrar por rol"),
    status: Optional[UserStatus] = Query(None, description="Filtrar por estado"),
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Obtener lista de usuarios con paginación y filtros.
    Solo los administradores pueden listar usuarios.
    """
    return await user_controller.get_users(page, limit, search, role, status)

@router.get("/stats", summary="Obtener estadísticas básicas de usuarios")
async def get_user_stats(current_user: UserResponse = Depends(get_current_user)):
    """
    Obtener estadísticas básicas del sistema.
    Accesible para usuarios autenticados.
    """
    try:
        # Obtener total de usuarios
        total_users = user_controller.collection.count_documents({})
        
        # Crear respuesta con estadísticas básicas
        stats = {
            "total_users": total_users,
            "system_status": "active",
            "database_status": "connected"
        }
        
        return stats
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )


@router.get("/stats/roles", summary="Distribución de usuarios por rol")
async def stats_roles(current_admin: UserResponse = Depends(get_current_admin_user)):
    data = await user_controller.get_role_distribution()
    labels = [d['role'] for d in data]
    counts = [d['count'] for d in data]
    return {"success": True, "data": {"labels": labels, "datasets": [{"label": "Usuarios", "data": counts}]}}


@router.get("/stats/registrations", summary="Altas de usuarios por periodo")
async def stats_registrations(
    period: str = Query('month'),
    start: Optional[str] = None,
    end: Optional[str] = None,
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    # parse start/end if given
    s = None
    e = None
    from datetime import datetime
    if start:
        s = datetime.fromisoformat(start)
    if end:
        e = datetime.fromisoformat(end)
    payload = await user_controller.get_registrations(period=period, start=s, end=e)
    return {"success": True, "data": {"labels": payload['labels'], "datasets": [{"label": "Altas", "data": payload['data']}]}}


@router.get("/stats/last_logins", summary="Buckets de últimos logins")
async def stats_last_logins(current_admin: UserResponse = Depends(get_current_admin_user)):
    payload = await user_controller.get_last_login_buckets()
    return {"success": True, "data": {"labels": payload['labels'], "datasets": [{"label": "Usuarios", "data": payload['data']}]} }


@router.get("/stats/departments", summary="Top departamentos por número de usuarios")
async def stats_departments(top: int = Query(10, ge=1, le=100), current_admin: UserResponse = Depends(get_current_admin_user)):
    payload = await user_controller.get_departments_top(top=top)
    return {"success": True, "data": {"labels": payload['labels'], "datasets": [{"label": "Usuarios", "data": payload['data']}]}}

@router.get("/{user_id}", response_model=UserResponse, summary="Obtener usuario por ID")
async def get_user(
    user_id: str,
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Obtener un usuario específico por ID.
    Solo los administradores pueden ver usuarios.
    """
    user = await user_controller.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user

@router.put("/{user_id}", response_model=UserResponse, summary="Actualizar usuario")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Actualizar un usuario existente.
    Solo los administradores pueden actualizar usuarios.
    """
    user = await user_controller.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user

@router.delete("/{user_id}", summary="Eliminar usuario")
async def delete_user(
    user_id: str,
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Eliminar un usuario.
    Solo los administradores pueden eliminar usuarios.
    """
    success = await user_controller.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return {"message": "Usuario eliminado exitosamente"}

# Rutas adicionales
@router.get("/search/{term}", response_model=List[UserResponse], summary="Buscar usuarios")
async def search_users(
    term: str,
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Buscar usuarios por término de búsqueda.
    Solo los administradores pueden buscar usuarios.
    """
    result = await user_controller.get_users(search=term, limit=50)
    return result.users

@router.patch("/{user_id}/status", response_model=UserResponse, summary="Cambiar estado de usuario")
async def change_user_status(
    user_id: str,
    status: UserStatus,
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Cambiar el estado de un usuario (activo, inactivo, suspendido).
    Solo los administradores pueden cambiar estados.
    """
    user_update = UserUpdate(status=status)
    user = await user_controller.update_user(user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user

@router.patch("/{user_id}/role", response_model=UserResponse, summary="Cambiar rol de usuario")
async def change_user_role(
    user_id: str,
    role: UserRole,
    current_admin: UserResponse = Depends(get_current_admin_user)
):
    """
    Cambiar el rol de un usuario (admin, solicitante).
    Solo los administradores pueden cambiar roles.
    """
    user_update = UserUpdate(role=role)
    user = await user_controller.update_user(user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user