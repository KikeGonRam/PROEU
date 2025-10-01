"""
Sistema de rangos y permisos para usuarios
"""
from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel

class UserRole(str, Enum):
    """Roles de usuario del sistema"""
    ADMIN = "admin"
    SOLICITANTE = "solicitante"
    SUPERVISOR = "supervisor"
    CONTADOR = "contador"

class Permission(str, Enum):
    """Permisos específicos del sistema"""
    # Gestión de usuarios
    USER_CREATE = "user:create"
    USER_READ = "user:read" 
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_LIST = "user:list"
    
    # Gestión de solicitudes
    REQUEST_CREATE = "request:create"
    REQUEST_READ = "request:read"
    REQUEST_UPDATE = "request:update"
    REQUEST_DELETE = "request:delete"
    REQUEST_LIST = "request:list"
    REQUEST_APPROVE = "request:approve"
    REQUEST_REJECT = "request:reject"
    
    # Reportes y estadísticas
    REPORT_VIEW = "report:view"
    REPORT_EXPORT = "report:export"
    STATS_VIEW = "stats:view"
    
    # Configuración del sistema
    SYSTEM_CONFIG = "system:config"
    SYSTEM_LOGS = "system:logs"

class RolePermissions(BaseModel):
    """Mapeo de roles a permisos"""
    role: UserRole
    permissions: List[Permission]
    description: str

# Definición de permisos por rol
ROLE_PERMISSIONS: Dict[UserRole, RolePermissions] = {
    UserRole.ADMIN: RolePermissions(
        role=UserRole.ADMIN,
        description="Administrador del sistema con acceso completo",
        permissions=[
            # Usuarios - Control total
            Permission.USER_CREATE,
            Permission.USER_READ,
            Permission.USER_UPDATE,
            Permission.USER_DELETE,
            Permission.USER_LIST,
            
            # Solicitudes - Control total
            Permission.REQUEST_CREATE,
            Permission.REQUEST_READ,
            Permission.REQUEST_UPDATE,
            Permission.REQUEST_DELETE,
            Permission.REQUEST_LIST,
            Permission.REQUEST_APPROVE,
            Permission.REQUEST_REJECT,
            
            # Reportes y estadísticas
            Permission.REPORT_VIEW,
            Permission.REPORT_EXPORT,
            Permission.STATS_VIEW,
            
            # Sistema
            Permission.SYSTEM_CONFIG,
            Permission.SYSTEM_LOGS,
        ]
    ),
    
    UserRole.SUPERVISOR: RolePermissions(
        role=UserRole.SUPERVISOR,
        description="Supervisor con permisos de aprobación y gestión",
        permissions=[
            # Usuarios - Solo lectura
            Permission.USER_READ,
            Permission.USER_LIST,
            
            # Solicitudes - Gestión y aprobación
            Permission.REQUEST_CREATE,
            Permission.REQUEST_READ,
            Permission.REQUEST_UPDATE,
            Permission.REQUEST_LIST,
            Permission.REQUEST_APPROVE,
            Permission.REQUEST_REJECT,
            
            # Reportes
            Permission.REPORT_VIEW,
            Permission.STATS_VIEW,
        ]
    ),
    
    UserRole.CONTADOR: RolePermissions(
        role=UserRole.CONTADOR,
        description="Contador con permisos de gestión financiera",
        permissions=[
            # Usuarios - Solo lectura
            Permission.USER_READ,
            Permission.USER_LIST,
            
            # Solicitudes - Lectura y gestión
            Permission.REQUEST_READ,
            Permission.REQUEST_UPDATE,
            Permission.REQUEST_LIST,
            
            # Reportes completos
            Permission.REPORT_VIEW,
            Permission.REPORT_EXPORT,
            Permission.STATS_VIEW,
        ]
    ),
    
    UserRole.SOLICITANTE: RolePermissions(
        role=UserRole.SOLICITANTE,
        description="Usuario solicitante con permisos básicos",
        permissions=[
            # Usuarios - Solo su perfil
            Permission.USER_READ,
            
            # Solicitudes - Solo sus solicitudes
            Permission.REQUEST_CREATE,
            Permission.REQUEST_READ,
            Permission.REQUEST_UPDATE,
            Permission.REQUEST_LIST,
        ]
    ),
}

def get_user_permissions(role: UserRole) -> List[Permission]:
    """Obtener permisos de un rol específico"""
    role_info = ROLE_PERMISSIONS.get(role)
    return role_info.permissions if role_info else []

def user_has_permission(user_role: UserRole, permission: Permission) -> bool:
    """Verificar si un usuario tiene un permiso específico"""
    user_permissions = get_user_permissions(user_role)
    return permission in user_permissions

def get_role_description(role: UserRole) -> str:
    """Obtener descripción de un rol"""
    role_info = ROLE_PERMISSIONS.get(role)
    return role_info.description if role_info else "Rol desconocido"

def get_available_roles() -> List[Dict[str, Any]]:
    """Obtener lista de roles disponibles con información"""
    return [
        {
            "value": role.value,
            "label": role.value.title(),
            "description": role_info.description,
            "permissions_count": len(role_info.permissions)
        }
        for role, role_info in ROLE_PERMISSIONS.items()
    ]

# Jerarquía de roles (mayor número = mayor autoridad)
ROLE_HIERARCHY = {
    UserRole.SOLICITANTE: 1,
    UserRole.CONTADOR: 2,
    UserRole.SUPERVISOR: 3,
    UserRole.ADMIN: 4,
}

def user_can_manage_role(manager_role: UserRole, target_role: UserRole) -> bool:
    """Verificar si un usuario puede gestionar otro rol"""
    manager_level = ROLE_HIERARCHY.get(manager_role, 0)
    target_level = ROLE_HIERARCHY.get(target_role, 0)
    return manager_level > target_level

def get_manageable_roles(user_role: UserRole) -> List[UserRole]:
    """Obtener roles que un usuario puede gestionar"""
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    return [
        role for role, level in ROLE_HIERARCHY.items()
        if level < user_level
    ]