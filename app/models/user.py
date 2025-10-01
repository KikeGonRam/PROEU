from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from bson import ObjectId

class UserRole(str, Enum):
    ADMIN = "admin"
    SOLICITANTE = "solicitante"
    SUPERVISOR = "supervisor"
    CONTADOR = "contador"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

# Esquema base para User
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email del usuario")
    first_name: str = Field(..., min_length=2, max_length=50, description="Nombre del usuario")
    last_name: str = Field(..., min_length=2, max_length=50, description="Apellido del usuario")
    department: str = Field(..., min_length=2, max_length=100, description="Departamento del usuario")
    phone: Optional[str] = Field(None, min_length=10, max_length=20, description="Teléfono del usuario")
    role: UserRole = Field(default=UserRole.SOLICITANTE, description="Rol del usuario")
    status: UserStatus = Field(default=UserStatus.ACTIVE, description="Estado del usuario")

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError('Teléfono debe contener solo números, +, - y espacios')
        return v

# Esquema para crear usuario
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Contraseña del usuario")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v

# Esquema para actualizar usuario
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    password: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v and len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v

# Esquema para respuesta de usuario (sin contraseña)
class UserResponse(UserBase):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    @field_validator('id', mode='before')
    @classmethod
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str, datetime: lambda dt: dt.isoformat()}
    }

# Esquema para usuario en base de datos
class UserInDB(UserResponse):
    hashed_password: str

# Esquema para login
class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., description="Contraseña del usuario")

# Esquema para token
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Esquema para datos del token
class TokenData(BaseModel):
    email: Optional[str] = None

# Esquema para respuesta de lista de usuarios con paginación
class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    limit: int
    total_pages: int