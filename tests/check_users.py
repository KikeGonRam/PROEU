#!/usr/bin/env python3
"""
Script para verificar usuarios en la base de datos
"""
from app.config.database import get_database_sync

def check_users():
    """Verificar usuarios en la base de datos"""
    try:
        db = get_database_sync()
        users = list(db.users.find({}, {'email': 1, 'role': 1, 'first_name': 1, 'last_name': 1, '_id': 0}))
        
        print("👥 Usuarios en la base de datos:")
        print("=" * 40)
        
        if not users:
            print("❌ No hay usuarios en la base de datos")
            return
        
        for i, user in enumerate(users, 1):
            print(f"{i}. Email: {user.get('email')}")
            print(f"   Nombre: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}")
            print(f"   Rol: {user.get('role', 'N/A')}")
            print()
        
        print(f"Total de usuarios: {len(users)}")
        
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")

if __name__ == "__main__":
    check_users()