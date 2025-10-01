#!/usr/bin/env python3
"""
Script para verificar el estado de autenticación
"""
import requests

def check_auth_status():
    """Verificar el estado de autenticación"""
    print("🔍 Verificando estado de autenticación...")
    print("=" * 50)
    
    # 1. Verificar que el login funciona
    print("\n1. 🔑 Probando login...")
    login_data = {
        "email": "admin@utvt.edu.mx",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post("http://localhost:8000/api/users/login", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            user = token_data.get("user")
            
            print("✅ Login exitoso")
            print(f"   Token: {token[:20]}...")
            print(f"   Usuario: {user.get('first_name')} {user.get('last_name')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Rol: {user.get('role')}")
            
            # 2. Probar acceso a usuarios con el token
            print("\n2. 👥 Probando acceso a usuarios...")
            headers = {"Authorization": f"Bearer {token}"}
            
            users_response = requests.get("http://localhost:8000/api/users", headers=headers)
            
            if users_response.status_code == 200:
                users_data = users_response.json()
                print("✅ Acceso a usuarios exitoso")
                print(f"   Total usuarios: {users_data.get('total')}")
            else:
                print(f"❌ Error accediendo a usuarios: {users_response.status_code}")
                print(f"   Respuesta: {users_response.text}")
            
            # 3. Probar acceso sin token
            print("\n3. 🚫 Probando acceso sin token...")
            no_token_response = requests.get("http://localhost:8000/api/users")
            
            if no_token_response.status_code == 401:
                print("✅ Seguridad funcionando - Sin token = 401")
            else:
                print(f"⚠️ Problema de seguridad - Sin token = {no_token_response.status_code}")
            
            # 4. Probar con token inválido
            print("\n4. 🔒 Probando con token inválido...")
            bad_headers = {"Authorization": "Bearer token_invalido"}
            bad_token_response = requests.get("http://localhost:8000/api/users", headers=bad_headers)
            
            if bad_token_response.status_code == 401:
                print("✅ Seguridad funcionando - Token inválido = 401")
            else:
                print(f"⚠️ Problema de seguridad - Token inválido = {bad_token_response.status_code}")
            
        else:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"   Respuesta: {login_response.text}")
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("\n" + "=" * 50)
    print("💡 Diagnóstico:")
    print("   - Si login funciona pero la página web da 401:")
    print("     🔍 Verificar que el token se guarde en localStorage")
    print("     🔍 Verificar que auth.js esté cargando el token")
    print("     🔍 Verificar que el usuario esté logueado en el navegador")
    print("   - Solución: Ir a /login e iniciar sesión nuevamente")

if __name__ == "__main__":
    check_auth_status()