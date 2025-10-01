from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.user import (
    UserCreate, UserUpdate, UserResponse, UserLogin, 
    Token, UserListResponse, UserRole, UserStatus
)
from app.controllers.user_controller import user_controller

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
async def login(login_data: UserLogin):
    """
    Iniciar sesión con email y contraseña.
    Retorna un token JWT para autenticación.
    """
    return await user_controller.login(login_data)

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
    limit: int = Query(10, ge=1, le=100, description="Elementos por página"),
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