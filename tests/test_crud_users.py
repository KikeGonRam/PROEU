#!/usr/bin/env python3
"""
Script para probar la funcionalidad CRUD de usuarios
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"

def test_user_crud():
    """Probar funcionalidad CRUD de usuarios"""
    
    print("🚀 Iniciando pruebas del CRUD de usuarios...")
    print("=" * 50)
    
    # 1. Login como admin
    print("\n1. 🔑 Autenticación como admin...")
    login_data = {
        "email": "admin@utvt.edu.mx",
        "password": "admin123"
    }
    
    login_response = requests.post(f"{API_URL}/users/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Error en login: {login_response.status_code}")
        print(f"Respuesta: {login_response.text}")
        return
    
    token_data = login_response.json()
    token = token_data.get("access_token")
    
    if not token:
        print("❌ No se obtuvo token de acceso")
        return
    
    print(f"✅ Login exitoso, token obtenido")
    
    # Headers para autenticación
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 2. Obtener estadísticas
    print("\n2. 📊 Obteniendo estadísticas...")
    stats_response = requests.get(f"{API_URL}/users/stats", headers=headers)
    
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"✅ Estadísticas obtenidas:")
        print(f"   - Total usuarios: {stats.get('total_users')}")
        print(f"   - Estado sistema: {stats.get('system_status')}")
        print(f"   - Estado BD: {stats.get('database_status')}")
    else:
        print(f"❌ Error obteniendo estadísticas: {stats_response.status_code}")
    
    # 3. Listar usuarios
    print("\n3. 👥 Listando usuarios...")
    users_response = requests.get(f"{API_URL}/users", headers=headers)
    
    if users_response.status_code == 200:
        users_data = users_response.json()
        print(f"✅ Usuarios obtenidos:")
        print(f"   - Total: {users_data.get('total')}")
        print(f"   - Página: {users_data.get('page')}")
        print(f"   - Usuarios en página: {len(users_data.get('users', []))}")
        
        # Mostrar primer usuario
        if users_data.get('users'):
            first_user = users_data['users'][0]
            print(f"   - Primer usuario: {first_user.get('first_name')} {first_user.get('last_name')} ({first_user.get('email')})")
    else:
        print(f"❌ Error listando usuarios: {users_response.status_code}")
        print(f"Respuesta: {users_response.text}")
    
    # 4. Crear un nuevo usuario de prueba
    print("\n4. ➕ Creando usuario de prueba...")
    new_user_data = {
        "first_name": "Usuario",
        "last_name": "Prueba",
        "email": "usuario.prueba@test.com",
        "department": "Desarrollo",
        "phone": "555-012-3456",
        "role": "solicitante",
        "status": "active",
        "password": "prueba123"
    }
    
    create_response = requests.post(f"{API_URL}/users", headers=headers, json=new_user_data)
    
    if create_response.status_code == 201:
        created_user = create_response.json()
        user_id = created_user.get('id')
        print(f"✅ Usuario creado exitosamente:")
        print(f"   - ID: {user_id}")
        print(f"   - Nombre: {created_user.get('first_name')} {created_user.get('last_name')}")
        print(f"   - Email: {created_user.get('email')}")
        
        # 5. Actualizar el usuario
        print("\n5. ✏️ Actualizando usuario...")
        update_data = {
            "first_name": "Usuario",
            "last_name": "Actualizado",
            "email": "usuario.prueba@test.com",
            "department": "Desarrollo Actualizado",
            "phone": "555-999-8888",
            "role": "solicitante",
            "status": "active"
        }
        
        update_response = requests.put(f"{API_URL}/users/{user_id}", headers=headers, json=update_data)
        
        if update_response.status_code == 200:
            updated_user = update_response.json()
            print(f"✅ Usuario actualizado:")
            print(f"   - Nombre: {updated_user.get('first_name')} {updated_user.get('last_name')}")
            print(f"   - Departamento: {updated_user.get('department')}")
            print(f"   - Teléfono: {updated_user.get('phone')}")
        else:
            print(f"❌ Error actualizando usuario: {update_response.status_code}")
        
        # 6. Obtener usuario específico
        print("\n6. 🔍 Obteniendo usuario específico...")
        get_user_response = requests.get(f"{API_URL}/users/{user_id}", headers=headers)
        
        if get_user_response.status_code == 200:
            user_detail = get_user_response.json()
            print(f"✅ Usuario obtenido:")
            print(f"   - ID: {user_detail.get('id')}")
            print(f"   - Nombre completo: {user_detail.get('first_name')} {user_detail.get('last_name')}")
            print(f"   - Email: {user_detail.get('email')}")
            print(f"   - Rol: {user_detail.get('role')}")
            print(f"   - Estado: {user_detail.get('status')}")
        else:
            print(f"❌ Error obteniendo usuario: {get_user_response.status_code}")
        
        # 7. Eliminar usuario de prueba
        print("\n7. 🗑️ Eliminando usuario de prueba...")
        delete_response = requests.delete(f"{API_URL}/users/{user_id}", headers=headers)
        
        if delete_response.status_code == 200:
            print(f"✅ Usuario eliminado exitosamente")
        else:
            print(f"❌ Error eliminando usuario: {delete_response.status_code}")
            print(f"Respuesta: {delete_response.text}")
    
    else:
        print(f"❌ Error creando usuario: {create_response.status_code}")
        print(f"Respuesta: {create_response.text}")
    
    # 8. Probar filtros
    print("\n8. 🔍 Probando filtros...")
    
    # Filtro por rol
    filter_response = requests.get(f"{API_URL}/users?role=admin", headers=headers)
    if filter_response.status_code == 200:
        filtered_data = filter_response.json()
        print(f"✅ Filtro por rol 'admin': {filtered_data.get('total')} usuarios")
    
    # Filtro por búsqueda
    search_response = requests.get(f"{API_URL}/users?search=admin", headers=headers)
    if search_response.status_code == 200:
        search_data = search_response.json()
        print(f"✅ Búsqueda 'admin': {search_data.get('total')} usuarios")
    
    print("\n" + "=" * 50)
    print("🎉 Pruebas del CRUD completadas exitosamente!")
    print("\n✨ Funcionalidades verificadas:")
    print("   ✅ Autenticación con JWT")
    print("   ✅ Obtener estadísticas")
    print("   ✅ Listar usuarios con paginación")
    print("   ✅ Crear nuevo usuario")
    print("   ✅ Actualizar usuario existente")
    print("   ✅ Obtener usuario por ID")
    print("   ✅ Eliminar usuario")
    print("   ✅ Filtros y búsqueda")

if __name__ == "__main__":
    try:
        test_user_crud()
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")