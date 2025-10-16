"""
Middleware de autenticación y autorización
"""
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Callable

from app.models.user import UserResponse
from app.controllers.user_controller import user_controller

# Configurar seguridad
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Obtener usuario actual desde el token JWT
    
    Args:
        credentials: Credenciales HTTP Bearer
        
    Returns:
        Diccionario con información del usuario
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    email = user_controller.verify_token(credentials.credentials)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await user_controller.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Convertir a diccionario para facilitar el uso
    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "nombre": f"{user.first_name} {user.last_name}",  # Nombre completo para compatibilidad
        "role": user.role,
        "department": user.department,
        "is_active": user.status == "active"
    }


async def get_optional_current_user(request: Request) -> dict | None:
    """
    Optional current user dependency. Returns None if no Authorization header is provided
    or the token is invalid. Useful for pages that are public but can show user info
    when the visitor is authenticated.
    """
    # If there's no credentials (no Authorization header) the HTTPBearer dependency
    # will raise automatically. To allow optional, we must catch that case by
    # inspecting the incoming header via a try/except usage of the security dependency.
    # Read Authorization header manually — if missing, return None (public page)
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth_header:
        return None

    # Use HTTPBearer to parse/validate the header and obtain credentials
    try:
        credentials = await security(request)
    except Exception:
        # invalid or malformed header
        return None

    # If credentials present, verify token
    email = user_controller.verify_token(credentials.credentials)
    if email is None:
        return None

    user = await user_controller.get_user_by_email(email)
    if user is None:
        return None

    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "nombre": f"{user.first_name} {user.last_name}",
        "role": user.role,
        "department": user.department,
        "is_active": user.status == "active"
    }


def require_role(required_role: str) -> Callable:
    """
    Dependency factory para requerir un rol específico
    
    Args:
        required_role: Rol requerido ("admin", "solicitante", "aprobador", "pagador")
        
    Returns:
        Función de dependency que valida el rol
        
    Example:
        @router.get("/admin-only")
        async def admin_endpoint(user: dict = Depends(require_role("admin"))):
            return {"message": "Solo admins pueden ver esto"}
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        """
        Verifica que el usuario tenga el rol requerido
        
        Args:
            current_user: Usuario actual obtenido del token
            
        Returns:
            Diccionario con información del usuario
            
        Raises:
            HTTPException: Si el usuario no tiene el rol requerido
        """
        if current_user["role"] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere rol: {required_role}. Tu rol es: {current_user['role']}"
            )
        
        if not current_user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tu cuenta está inactiva. Contacta al administrador."
            )
        
        return current_user
    
    return role_checker


def require_any_role(*roles: str) -> Callable:
    """
    Dependency factory para requerir uno de varios roles
    
    Args:
        *roles: Lista de roles permitidos
        
    Returns:
        Función de dependency que valida los roles
        
    Example:
        @router.get("/multi-role")
        async def multi_role_endpoint(
            user: dict = Depends(require_any_role("admin", "aprobador"))
        ):
            return {"message": "Admins y aprobadores pueden ver esto"}
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        """
        Verifica que el usuario tenga uno de los roles requeridos
        
        Args:
            current_user: Usuario actual obtenido del token
            
        Returns:
            Diccionario con información del usuario
            
        Raises:
            HTTPException: Si el usuario no tiene ninguno de los roles requeridos
        """
        if current_user["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Roles permitidos: {', '.join(roles)}. Tu rol es: {current_user['role']}"
            )
        
        if not current_user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tu cuenta está inactiva. Contacta al administrador."
            )
        
        return current_user
    
    return role_checker


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency para requerir rol de administrador
    
    Args:
        current_user: Usuario actual obtenido del token
        
    Returns:
        Diccionario con información del usuario
        
    Raises:
        HTTPException: Si el usuario no es administrador
    """
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol de administrador."
        )
    
    return current_user


async def require_solicitante(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency para requerir rol de solicitante
    
    Args:
        current_user: Usuario actual obtenido del token
        
    Returns:
        Diccionario con información del usuario
        
    Raises:
        HTTPException: Si el usuario no es solicitante
    """
    if current_user["role"] != "solicitante":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol de solicitante."
        )
    
    return current_user


async def require_aprobador(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency para requerir rol de aprobador
    
    Args:
        current_user: Usuario actual obtenido del token
        
    Returns:
        Diccionario con información del usuario
        
    Raises:
        HTTPException: Si el usuario no es aprobador
    """
    if current_user["role"] != "aprobador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol de aprobador."
        )
    
    return current_user


async def require_pagador(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency para requerir rol de pagador
    
    Args:
        current_user: Usuario actual obtenido del token
        
    Returns:
        Diccionario con información del usuario
        
    Raises:
        HTTPException: Si el usuario no es pagador
    """
    if current_user["role"] != "pagador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol de pagador."
        )
    
    return current_user
