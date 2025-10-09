from pymongo import MongoClient
from datetime import datetime
import bcrypt

MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "sistema_solicitudes_pagos"

def hash_password(password):
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")

def init_database():
    try:
        client = MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        
        print("Inicializando base de datos...")
        db.users.delete_many({})
        db.users.create_index([("email", 1)], unique=True)
        
        users_data = [
            {
                "email": "admin@utvt.edu.mx",
                "hashed_password": hash_password("admin123"),
                "first_name": "Admin",
                "last_name": "Sistema",
                "department": "TI",
                "phone": "+52 722 123 4567",
                "role": "admin",
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": None
            },
            {
                "email": "solicitante@utvt.edu.mx",
                "hashed_password": hash_password("solicitante123"),
                "first_name": "Juan Carlos",
                "last_name": "Solicitante",
                "department": "Finanzas",
                "phone": "+52 722 555 0001",
                "role": "solicitante",
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": None
            }
        ]
        
        result = db.users.insert_many(users_data)
        print(f"Usuarios creados: {len(result.inserted_ids)}")
        
        print("CREDENCIALES:")
        print("admin@utvt.edu.mx / admin123 (Administrador)")
        print("solicitante@utvt.edu.mx / solicitante123 (Solicitante)")
        
        client.close()
        print("Base de datos inicializada!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    init_database()
