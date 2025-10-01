# Test rápido para verificar la ruta /stats
import requests
import json

def test_stats_route():
    """Probar la ruta de estadísticas"""
    
    # Primero hacer login para obtener token
    login_url = "http://localhost:8000/api/users/login"
    login_data = {
        "email": "admin@utvt.edu.mx",
        "password": "admin123"
    }
    
    print("🔐 Intentando login...")
    try:
        login_response = requests.post(login_url, json=login_data)
        print(f"Login response status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print("✅ Login exitoso")
            
            # Ahora probar la ruta de estadísticas
            stats_url = "http://localhost:8000/api/users/stats"
            headers = {"Authorization": f"Bearer {token}"}
            
            print("\n📊 Probando ruta de estadísticas...")
            stats_response = requests.get(stats_url, headers=headers)
            print(f"Stats response status: {stats_response.status_code}")
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                print("✅ Estadísticas obtenidas correctamente:")
                print(json.dumps(stats_data, indent=2))
            else:
                print(f"❌ Error en estadísticas: {stats_response.text}")
        
        else:
            print(f"❌ Error en login: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    test_stats_route()