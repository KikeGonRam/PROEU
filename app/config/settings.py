import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "sistema_solicitudes_pagos"
    
    # JWT
    SECRET_KEY: str = "tu-clave-secreta-muy-segura-aqui-cambiar-en-produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Aplicación
    DEBUG: bool = True
    
    model_config = {"env_file": ".env"}

# Instancia global de configuración
settings = Settings()