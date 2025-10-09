# -*- coding: utf-8 -*-
"""
Script para corregir la versión de PySpark
Instala PySpark 3.4.4 compatible con Java 8
"""
import sys
import subprocess

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'ignore').decode('ascii'))

safe_print("=" * 60)
safe_print("🔧 CORRECCIÓN DE VERSIÓN DE PYSPARK")
safe_print("=" * 60)

safe_print("\n❌ Problema detectado:")
safe_print("   PySpark 4.0.1 NO es compatible con Java 8")
safe_print("   Java 8 requiere PySpark 3.x")

safe_print("\n🔄 Desinstalando PySpark 4.0.1...")
try:
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "pyspark"], 
                   check=True)
    safe_print("   ✅ PySpark 4.0.1 desinstalado")
except Exception as e:
    safe_print(f"   ⚠️ Error: {e}")

safe_print("\n📦 Instalando PySpark 3.4.4 (compatible con Java 8)...")
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "pyspark==3.4.4"], 
                   check=True)
    safe_print("   ✅ PySpark 3.4.4 instalado correctamente")
except Exception as e:
    safe_print(f"   ❌ Error instalando: {e}")
    safe_print("\n💡 Ejecuta manualmente:")
    safe_print("   pip uninstall -y pyspark")
    safe_print("   pip install pyspark==3.4.4")
    sys.exit(1)

safe_print("\n🧪 Verificando instalación...")
try:
    import pyspark
    safe_print(f"   ✅ PySpark version: {pyspark.__version__}")
    
    if pyspark.__version__.startswith("3."):
        safe_print("\n" + "=" * 60)
        safe_print("🎉 ¡CORRECCIÓN EXITOSA!")
        safe_print("✅ PySpark 3.4.4 ahora es compatible con Java 8")
        safe_print("✅ Puedes ejecutar la GUI de nuevo")
        safe_print("=" * 60)
    else:
        safe_print(f"\n⚠️ Versión instalada: {pyspark.__version__}")
        safe_print("   Se esperaba PySpark 3.x")
        
except Exception as e:
    safe_print(f"   ❌ Error verificando: {e}")
    sys.exit(1)
