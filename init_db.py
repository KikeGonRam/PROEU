# Script para inicializar la base de datos con datos de ejemplo
from pymongo import MongoClient
from datetime import datetime
import bcrypt
import os
from bson import ObjectId

# Configuración de conexión
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "sistema_solicitudes_pagos"

def hash_password(password: str) -> str:
    """Crear hash de contraseña usando bcrypt directamente con validación"""
    # Validar y truncar la contraseña si es necesaria
    if len(password) > 72:
        password = password[:72]
    
    # Asegurar que la contraseña esté en bytes
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Crear hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def init_database():
    """Inicializar base de datos con datos de ejemplo"""
    try:
        # Conectar a MongoDB
        client = MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        
        print("🚀 Inicializando base de datos...")
        
        # Limpiar colecciones existentes (opcional)
        print("🧹 Limpiando datos existentes...")
        db.users.delete_many({})
        
        # Crear índices
        print("📋 Creando índices...")
        db.users.create_index([("email", 1)], unique=True)
        db.users.create_index([("created_at", -1)])
        
        # Crear usuario administrador
        print("� Creando usuario administrador...")
        
        admin_user = {
            "email": "admin@utvt.edu.mx",
            "hashed_password": hash_password("admin123"),
            "first_name": "Administrador",
            "last_name": "Sistema",
            "department": "Tecnologías de la Información",
            "phone": "+52 722 123 4567",
            "role": "admin",
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None
        }
        
        # Insertar usuario administrador
        result = db.users.insert_one(admin_user)
        print("✅ 1 usuario administrador creado exitosamente")
        
        # Mostrar información de login
        print("\n" + "="*60)
        print("🔐 INFORMACIÓN DE ACCESO")
        print("="*60)
        print("Usuario Administrador:")
        print("  Email: admin@utvt.edu.mx")
        print("  Contraseña: admin123")
        print("  Rol: Administrador")
        print("  Departamento: Tecnologías de la Información")
        
        print("\n" + "="*60)
        print("🌐 ACCESO A LA APLICACIÓN")
        print("="*60)
        print("Aplicación Web: http://localhost:8000")
        print("Login: http://localhost:8000/login")
        print("Dashboard: http://localhost:8000/home")
        print("Documentación API: http://localhost:8000/docs")
        print("="*60)
        
        client.close()
        print("✅ Base de datos inicializada correctamente con usuario único")
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")

if __name__ == "__main__":
    init_database()