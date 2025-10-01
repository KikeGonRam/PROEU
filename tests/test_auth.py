# Script para probar la autenticación
from pymongo import MongoClient
from passlib.context import CryptContext
import bcrypt

# Configuración
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "sistema_solicitudes_pagos"

# Contexto de passlib (como en el controlador)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_authentication():
    """Probar la autenticación con diferentes métodos"""
    try:
        # Conectar a la base de datos
        client = MongoClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        
        # Buscar el usuario administrador
        admin_user = db.users.find_one({"email": "admin@utvt.edu.mx"})
        
        if not admin_user:
            print("❌ Usuario admin no encontrado en la base de datos")
            return
        
        print("✅ Usuario admin encontrado:")
        print(f"   Email: {admin_user['email']}")
        print(f"   Hash almacenado: {admin_user['hashed_password'][:50]}...")
        
        # Contraseñas a probar
        test_password = "admin123"
        stored_hash = admin_user['hashed_password']
        
        print(f"\n🔍 Probando contraseña: '{test_password}'")
        
        # Método 1: Usando passlib (como en el controlador)
        print("\n--- Método 1: passlib (usado en el controlador) ---")
        try:
            result_passlib = pwd_context.verify(test_password, stored_hash)
            print(f"   Resultado passlib: {'✅ VÁLIDA' if result_passlib else '❌ INVÁLIDA'}")
        except Exception as e:
            print(f"   Error passlib: {e}")
        
        # Método 2: Usando bcrypt directamente
        print("\n--- Método 2: bcrypt directo ---")
        try:
            result_bcrypt = bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8'))
            print(f"   Resultado bcrypt: {'✅ VÁLIDA' if result_bcrypt else '❌ INVÁLIDA'}")
        except Exception as e:
            print(f"   Error bcrypt: {e}")
        
        # Crear nuevo hash con passlib para comparar
        print("\n--- Creando nuevo hash con passlib ---")
        try:
            new_hash = pwd_context.hash(test_password)
            print(f"   Nuevo hash: {new_hash[:50]}...")
            verify_new = pwd_context.verify(test_password, new_hash)
            print(f"   Verificación del nuevo hash: {'✅ VÁLIDA' if verify_new else '❌ INVÁLIDA'}")
        except Exception as e:
            print(f"   Error creando nuevo hash: {e}")
        
        # Verificar otros usuarios también
        print("\n--- Verificando otros usuarios ---")
        other_users = db.users.find({"email": {"$ne": "admin@utvt.edu.mx"}}).limit(2)
        for user in other_users:
            email = user['email']
            # Extraer contraseña del email (formato: prefijo123)
            password = email.split('@')[0].replace('.', '') + '123'
            try:
                result = pwd_context.verify(password, user['hashed_password'])
                print(f"   {email}: {'✅ VÁLIDA' if result else '❌ INVÁLIDA'}")
            except Exception as e:
                print(f"   {email}: Error - {e}")
                
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    test_authentication()