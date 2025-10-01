# Script para inicializar la base de datos con usuario administrador
from pymongo import MongoClient
from datetime import datetime
import bcrypt
import os
from bson import ObjectId

# Configuracion de conexion
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "sistema_solicitudes_pagos"

def hash_password(password: str) -> str:
    """Crear hash de contraseña usando bcrypt directamente con validacion"""
    # Validar y truncar la contraseña si es necesaria
    if len(password) > 72:
        password = password[:72]
    
    # Asegurar que la contraseña este en bytes
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Crear hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def init_database():
    """Inicializar base de datos con usuario administrador"""
    try:
        # Conectar a MongoDB
        client = MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        
        print(" Inicializando base de datos...")
        
        # Limpiar colecciones existentes (opcional)
        print(" Limpiando datos existentes...")
        db.users.delete_many({})
        
        # Crear indices
        print(" Creando indices...")
        db.users.create_index([("email", 1)], unique=True)
        db.users.create_index([("created_at", -1)])
        
        # Crear unico usuario administrador
        print(" Creando usuario administrador...")
        
        admin_user = {
            "email": "admin@utvt.edu.mx",
            "hashed_password": hash_password("admin123"),
            "first_name": "Admin",
            "last_name": "Sistema",
            "department": "Tecnologias de la Informacion",
            "phone": "+52 722 123 4567",
            "role": "admin",
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None
        }
        
        # Insertar usuario administrador
        result = db.users.insert_one(admin_user)
        print(" 1 usuario administrador creado exitosamente")
        
        # Mostrar informacion de acceso
        print("\n" + "="*60)
        print(" CREDENCIALES DE ACCESO AL SISTEMA")
        print("="*60)
        
        print("\n ADMINISTRADOR - Control total del sistema")
        print("  Email: admin@utvt.edu.mx")
        print("  Contraseña: admin123")
        print("  Departamento: Tecnologias de la Informacion")
        
        print("\n" + "="*60)
        print(" ACCESO A LA APLICACION")
        print("="*60)
        print("Aplicacion Web: http://localhost:8000")
        print("Login Page: http://localhost:8000/login")
        print("API Docs: http://localhost:8000/docs")
        print("Dashboard: http://localhost:8000/home")
        print("="*60)
        
        # Cerrar conexion
        client.close()
        
        print("\n Base de datos inicializada correctamente!")
        print(" Ya puedes acceder con las credenciales del administrador")
        print("\nℹ  Los demas usuarios los puedes crear desde la interfaz web")
        print("   usando la gestion de usuarios en /users")
        
    except Exception as e:
        print(f" Error al inicializar la base de datos: {e}")
        raise

if __name__ == "__main__":
    init_database()
