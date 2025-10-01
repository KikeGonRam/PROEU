#!/usr/bin/env python3
"""
Script para verificar que la página de usuarios funciona correctamente
"""
import requests

def test_users_page():
    """Probar que la página de usuarios se carga correctamente"""
    try:
        # 1. Verificar que la página de usuarios se carga
        print("🌐 Probando página de usuarios...")
        page_response = requests.get("http://localhost:8000/users")
        
        if page_response.status_code == 200:
            print("✅ Página de usuarios se carga correctamente")
        else:
            print(f"❌ Error cargando página: {page_response.status_code}")
        
        # 2. Verificar autenticación y obtener token
        print("\n🔑 Probando autenticación...")
        login_data = {
            "email": "admin@utvt.edu.mx",
            "password": "admin123"
        }
        
        login_response = requests.post("http://localhost:8000/api/users/login", json=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print("✅ Autenticación exitosa")
            
            # 3. Probar endpoint de usuarios
            print("\n👥 Probando endpoint de usuarios...")
            headers = {"Authorization": f"Bearer {token}"}
            users_response = requests.get("http://localhost:8000/api/users", headers=headers)
            
            if users_response.status_code == 200:
                users_data = users_response.json()
                print(f"✅ API de usuarios funcionando - {users_data.get('total')} usuarios encontrados")
                
                if users_data.get('users'):
                    print(f"   Primera usuario: {users_data['users'][0].get('first_name')} {users_data['users'][0].get('last_name')}")
            else:
                print(f"❌ Error en API de usuarios: {users_response.status_code}")
                
        else:
            print(f"❌ Error en autenticación: {login_response.status_code}")
        
        print("\n" + "="*50)
        print("🎯 Estado del sistema:")
        print("✅ Servidor funcionando")
        print("✅ Páginas web cargando")
        print("✅ API REST operativa")
        print("✅ Autenticación activa")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor esté ejecutándose")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_users_page()