# -*- coding: utf-8 -*-
"""
Test simple de Spark - Diagnóstico
"""
import sys

# Configurar UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

def safe_print(text):
    """Imprimir texto de forma segura"""
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', 'ignore').decode('ascii'))

safe_print("=" * 60)
safe_print("🔍 DIAGNÓSTICO DE SPARK")
safe_print("=" * 60)

# Test 1: Verificar imports
safe_print("\n1. Verificando imports...")
try:
    import pyspark
    safe_print(f"   ✅ PySpark version: {pyspark.__version__}")
except Exception as e:
    safe_print(f"   ❌ Error importando PySpark: {e}")
    sys.exit(1)

# Test 2: Verificar Java
safe_print("\n2. Verificando Java...")
import subprocess
try:
    result = subprocess.run(['java', '-version'], 
                          capture_output=True, 
                          text=True,
                          encoding='utf-8',
                          errors='replace')
    java_output = result.stderr if result.stderr else result.stdout
    safe_print(f"   ✅ Java encontrado:")
    for line in java_output.split('\n')[:3]:
        if line.strip():
            safe_print(f"      {line.strip()}")
except Exception as e:
    safe_print(f"   ❌ Error verificando Java: {e}")

# Test 3: Variables de entorno
safe_print("\n3. Verificando variables de entorno...")
import os
spark_home = os.environ.get('SPARK_HOME', 'No configurado')
java_home = os.environ.get('JAVA_HOME', 'No configurado')
safe_print(f"   SPARK_HOME: {spark_home}")
safe_print(f"   JAVA_HOME: {java_home}")

# Test 4: Intentar crear SparkSession
safe_print("\n4. Intentando crear SparkSession...")
try:
    from pyspark.sql import SparkSession
    
    safe_print("   Creando SparkSession (puede tardar unos segundos)...")
    spark = SparkSession.builder \
        .appName("DiagnosticoSimple") \
        .master("local[1]") \
        .config("spark.ui.enabled", "false") \
        .config("spark.driver.host", "localhost") \
        .config("spark.driver.bindAddress", "127.0.0.1") \
        .getOrCreate()
    
    safe_print(f"   ✅ SparkSession creado exitosamente!")
    safe_print(f"   ✅ Spark Version: {spark.version}")
    safe_print(f"   ✅ Master: {spark.sparkContext.master}")
    
    # Test simple de operación
    safe_print("\n5. Test de operación simple...")
    data = [("Juan", 25), ("Maria", 30), ("Pedro", 35)]
    df = spark.createDataFrame(data, ["nombre", "edad"])
    count = df.count()
    safe_print(f"   ✅ DataFrame creado con {count} registros")
    
    # Mostrar datos
    safe_print("\n   Datos de prueba:")
    for row in df.collect():
        safe_print(f"      {row.nombre}: {row.edad} años")
    
    # Cerrar Spark
    spark.stop()
    safe_print("\n✅ Spark cerrado correctamente")
    
    safe_print("\n" + "=" * 60)
    safe_print("🎉 ¡TODOS LOS TESTS PASARON!")
    safe_print("✅ Spark está funcionando correctamente")
    safe_print("=" * 60)
    
except Exception as e:
    safe_print(f"   ❌ Error creando SparkSession: {e}")
    safe_print(f"   Tipo: {type(e).__name__}")
    
    import traceback
    safe_print("\n   Stack trace completo:")
    for line in traceback.format_exc().split('\n'):
        safe_print(f"   {line}")
    
    safe_print("\n" + "=" * 60)
    safe_print("❌ SPARK NO ESTÁ FUNCIONANDO CORRECTAMENTE")
    safe_print("=" * 60)
    sys.exit(1)
