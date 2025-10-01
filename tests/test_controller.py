# Script para probar el controlador actualizado
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.controllers.user_controller import UserController
import asyncio

async def test_controller_auth():
    """Probar la autenticación con el controlador actualizado"""
    try:
        controller = UserController()
        
        print("🔍 Probando autenticación con el controlador...")
        
        # Probar con admin
        print("\n--- Probando usuario admin ---")
        admin_user = await controller.authenticate_user("admin@utvt.edu.mx", "admin123")
        
        if admin_user:
            print("✅ Admin autenticado exitosamente!")
            print(f"   Nombre: {admin_user.first_name} {admin_user.last_name}")
            print(f"   Rol: {admin_user.role}")
            print(f"   Departamento: {admin_user.department}")
        else:
            print("❌ Admin NO pudo autenticarse")
        
        # Probar con usuario incorrecto
        print("\n--- Probando credenciales incorrectas ---")
        wrong_user = await controller.authenticate_user("admin@utvt.edu.mx", "wrong_password")
        
        if wrong_user:
            print("❌ ERROR: Usuario con contraseña incorrecta fue autenticado")
        else:
            print("✅ Credenciales incorrectas rechazadas correctamente")
        
        # Probar con otro usuario
        print("\n--- Probando otro usuario ---")
        other_user = await controller.authenticate_user("director.ti@utvt.edu.mx", "director123")
        
        if other_user:
            print("✅ Director TI autenticado exitosamente!")
            print(f"   Nombre: {other_user.first_name} {other_user.last_name}")
            print(f"   Rol: {other_user.role}")
        else:
            print("❌ Director TI NO pudo autenticarse")
            
        # Probar más usuarios
        print("\n--- Probando usuario de coordinación ---")
        coord_user = await controller.authenticate_user("coord.academica@utvt.edu.mx", "coord123")
        
        if coord_user:
            print("✅ Coordinadora autenticada exitosamente!")
            print(f"   Nombre: {coord_user.first_name} {coord_user.last_name}")
        else:
            print("❌ Coordinadora NO pudo autenticarse")
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")

if __name__ == "__main__":
    asyncio.run(test_controller_auth())