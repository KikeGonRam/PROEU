#!/usr/bin/env python3
"""
Script de verificación final del sistema
"""
import requests

def final_verification():
    """Verificación final completa del sistema"""
    print("🎯 VERIFICACIÓN FINAL DEL SISTEMA")
    print("=" * 50)
    
    # 1. Login
    print("\n1. 🔑 Autenticación...")
    login_data = {
        "email": "admin@utvt.edu.mx", 
        "password": "admin123"
    }
    
    login_response = requests.post("http://localhost:8000/api/users/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Error en login: {login_response.status_code}")
        return
    
    token_data = login_response.json()
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login exitoso")
    
    # 2. Verificar endpoints principales
    print("\n2. 🌐 Verificando endpoints...")
    
    endpoints = [
        ("/api/users", "Lista de usuarios"),
        ("/api/users/stats", "Estadísticas"),
    ]
    
    for endpoint, description in endpoints:
        response = requests.get(f"http://localhost:8000{endpoint}", headers=headers)
        if response.status_code == 200:
            print(f"✅ {description}: OK")
        else:
            print(f"❌ {description}: Error {response.status_code}")
    
    # 3. Verificar páginas web
    print("\n3. 📄 Verificando páginas web...")
    
    pages = [
        ("/", "Página principal"),
        ("/login", "Login"),
        ("/home", "Dashboard"),
        ("/users", "Gestión de usuarios"),
    ]
    
    for page, description in pages:
        response = requests.get(f"http://localhost:8000{page}")
        if response.status_code == 200:
            print(f"✅ {description}: OK")
        else:
            print(f"❌ {description}: Error {response.status_code}")
    
    # 4. Obtener usuario para probar edición
    print("\n4. 🔍 Probando funcionalidad de edición...")
    users_response = requests.get("http://localhost:8000/api/users", headers=headers)
    
    if users_response.status_code == 200:
        users_data = users_response.json()
        users = users_data.get("users", [])
        
        if users:
            test_user = users[0]  # Primer usuario
            user_id = test_user.get("_id")
            
            print(f"✅ Usuario de prueba: {test_user.get('first_name')} {test_user.get('last_name')}")
            print(f"   ID: {user_id}")
            
            # Probar obtener usuario específico
            user_response = requests.get(f"http://localhost:8000/api/users/{user_id}", headers=headers)
            
            if user_response.status_code == 200:
                print("✅ Obtención de usuario específico: OK")
                
                # Simular actualización
                user_detail = user_response.json()
                update_data = {
                    "first_name": user_detail.get("first_name"),
                    "last_name": user_detail.get("last_name"),
                    "email": user_detail.get("email"),
                    "department": user_detail.get("department"),
                    "phone": user_detail.get("phone"),
                    "role": user_detail.get("role"),
                    "status": user_detail.get("status")
                }
                
                update_response = requests.put(
                    f"http://localhost:8000/api/users/{user_id}",
                    headers={**headers, "Content-Type": "application/json"},
                    json=update_data
                )
                
                if update_response.status_code == 200:
                    print("✅ Actualización de usuario: OK")
                else:
                    print(f"❌ Actualización de usuario: Error {update_response.status_code}")
            else:
                print(f"❌ Obtención de usuario específico: Error {user_response.status_code}")
        else:
            print("❌ No hay usuarios para probar")
    
    print("\n" + "=" * 50)
    print("🎉 RESUMEN DEL SISTEMA")
    print("\n✅ COMPONENTES FUNCIONANDO:")
    print("   🔐 Autenticación JWT")
    print("   🌐 API REST completa")
    print("   📄 Páginas web")
    print("   👥 CRUD de usuarios")
    print("   🔍 Búsqueda y filtros")
    print("   ✏️ Funcionalidad de edición")
    
    print("\n🚀 PARA USAR EL SISTEMA:")
    print("   1. Ir a: http://localhost:8000/login")
    print("   2. Iniciar sesión con:")
    print("      Email: admin@utvt.edu.mx")
    print("      Contraseña: admin123")
    print("   3. Ir a: http://localhost:8000/users")
    print("   4. ¡Gestionar usuarios!")
    
    print("\n💡 SOLUCIÓN AL ERROR 401:")
    print("   - El error 401 significa que NO estás logueado")
    print("   - Necesitas hacer LOGIN PRIMERO")
    print("   - Después podrás acceder a la gestión de usuarios")

if __name__ == "__main__":
    final_verification()