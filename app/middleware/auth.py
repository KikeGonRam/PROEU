"""
Middleware para verificación de permisos
"""
from functools import wraps
from fastapi import HTTPException, status, Depends
from app.models.user import UserResponse
from app.utils.permissions import Permission, user_has_permission, UserRole
from app.routes.user_routes import get_current_user

def require_permission(permission: Permission):
    """
    Decorador para requerir un permiso específico
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Buscar el usuario actual en los kwargs
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, UserResponse):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            user_role = UserRole(current_user.role)
            
            if not user_has_permission(user_role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permisos insuficientes. Se requiere: {permission.value}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_admin():
    """
    Decorador para requerir permisos de administrador
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Buscar el usuario actual en los kwargs
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, UserResponse):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            if current_user.role != UserRole.ADMIN:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Se requieren permisos de administrador"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(*allowed_roles: UserRole):
    """
    Decorador para requerir uno de los roles especificados
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Buscar el usuario actual en los kwargs
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, UserResponse):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no autenticado"
                )
            
            user_role = UserRole(current_user.role)
            
            if user_role not in allowed_roles:
                allowed_roles_str = ", ".join([role.value for role in allowed_roles])
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Acceso denegado. Roles permitidos: {allowed_roles_str}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Dependencias FastAPI para permisos
def get_current_admin_user(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Dependency para obtener usuario administrador actual"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return current_user

def get_current_supervisor_or_admin(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Dependency para obtener usuario supervisor o administrador"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPERVISOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de supervisor o administrador"
        )
    return current_user

def check_user_permission(permission: Permission):
    """Factory para crear dependencies de verificación de permisos"""
    def verify_permission(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
        user_role = UserRole(current_user.role)
        
        if not user_has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permisos insuficientes. Se requiere: {permission.value}"
            )
        
        return current_user
    
    return verify_permission