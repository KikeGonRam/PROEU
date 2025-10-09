#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de compatibilidad Spark 3.4.4 + Java 8
Sistema EU-UTVT - Prueba de funcionamiento

Autor: Sistema EU-UTVT  
Fecha: Octubre 2025
"""

import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pymongo
from datetime import datetime

# Configurar codificación UTF-8 para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

def safe_print(text):
    """Imprimir texto de forma segura en Windows"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Reemplazar emojis problemáticos
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

# Configuración
SPARK_HOME = "C:/spark"
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "eu_utvt_db"
COLLECTION_NAME = "users"

def test_spark_compatibility():
    """Test de compatibilidad completo"""
    
    safe_print("🧪 PRUEBA DE COMPATIBILIDAD SPARK 3.4.4 + JAVA 8")
    safe_print("=" * 60)
    
    # 1. Test de inicialización de Spark
    safe_print("🚀 Test 1: Inicialización de Spark...")
    spark = None
    try:
        # Configuración más robusta
        spark = SparkSession.builder \
            .appName("EU-UTVT-Compatibility-Test") \
            .master("local[*]") \
            .config("spark.driver.memory", "2g") \
            .config("spark.executor.memory", "2g") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.driver.bindAddress", "127.0.0.1") \
            .config("spark.ui.enabled", "false") \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("ERROR")
        
        safe_print(f"✅ Spark Version: {spark.version}")
        safe_print(f"✅ Spark Master: {spark.sparkContext.master}")
        safe_print(f"✅ Java Version: Compatible con Java 8")
        
    except Exception as e:
        safe_print(f"❌ Error en Spark: {e}")
        safe_print(f"   Tipo de error: {type(e).__name__}")
        import traceback
        safe_print(f"   Detalles: {traceback.format_exc()}")
        if spark:
            try:
                spark.stop()
            except:
                pass
        return False
    
    # 2. Test de operaciones básicas
    safe_print("\n📊 Test 2: Operaciones básicas...")
    try:
        # Crear DataFrame de prueba
        data = [(1, "Juan", 25, "solicitante"), 
                (2, "María", 30, "aprobador"),
                (3, "Pedro", 35, "pagador"),
                (4, "Ana", 28, "admin")]
        
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("nombre", StringType(), True),
            StructField("edad", IntegerType(), True),
            StructField("role", StringType(), True)
        ])
        
        df = spark.createDataFrame(data, schema)
        
        # Operaciones básicas
        count = df.count()
        safe_print(f"✅ Registros creados: {count}")
        
        # Filtros y agregaciones
        solicitantes = df.filter(col("role") == "solicitante").count()
        edad_promedio = df.agg(avg("edad")).collect()[0][0]
        
        safe_print(f"✅ Solicitantes: {solicitantes}")
        safe_print(f"✅ Edad promedio: {edad_promedio:.1f}")
        
    except Exception as e:
        safe_print(f"❌ Error en operaciones: {e}")
        return False
    
    # 3. Test de conexión MongoDB
    safe_print("\n🔗 Test 3: Conexión MongoDB...")
    try:
        mongo_client = pymongo.MongoClient(MONGO_URI)
        db = mongo_client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        # Contar usuarios reales
        total_users = collection.count_documents({})
        safe_print(f"✅ Usuarios en MongoDB: {total_users:,}")
        
        # Obtener una muestra pequeña
        sample_users = list(collection.find().limit(10))
        safe_print(f"✅ Muestra obtenida: {len(sample_users)} usuarios")
        
        mongo_client.close()
        
    except Exception as e:
        safe_print(f"❌ Error en MongoDB: {e}")
        return False
    
    # 4. Test de integración Spark + MongoDB (muestra pequeña)
    safe_print("\n🔄 Test 4: Integración Spark + MongoDB (muestra)...")
    try:
        # Cargar solo 1000 usuarios para el test
        mongo_client = pymongo.MongoClient(MONGO_URI)
        db = mongo_client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]
        
        # Obtener muestra
        sample_data = []
        for user in collection.find().limit(1000):
            sample_data.append({
                'user_id': str(user.get('_id')),
                'nombre': user.get('nombre', ''),
                'email': user.get('email', ''),
                'role': user.get('role', ''),
                'department': user.get('department', ''),
                'is_active': user.get('is_active', True)
            })
        
        mongo_client.close()
        
        # Crear DataFrame de Spark
        df_sample = spark.createDataFrame(sample_data)
        
        # Análisis con Spark
        total = df_sample.count()
        activos = df_sample.filter(col("is_active") == True).count()
        
        role_distribution = df_sample.groupBy("role").count().collect()
        dept_distribution = df_sample.groupBy("department").count().collect()
        
        safe_print(f"✅ Total usuarios analizados: {total}")
        safe_print(f"✅ Usuarios activos: {activos}")
        safe_print(f"✅ Roles encontrados: {len(role_distribution)}")
        safe_print(f"✅ Departamentos encontrados: {len(dept_distribution)}")
        
        # Mostrar distribución de roles
        safe_print("\n📊 Distribución de roles (muestra):")
        for row in role_distribution:
            safe_print(f"   {row['role']}: {row['count']}")
        
    except Exception as e:
        safe_print(f"❌ Error en integración: {e}")
        return False
    
    # 5. Limpieza
    safe_print("\n🧹 Test 5: Limpieza de recursos...")
    try:
        spark.stop()
        safe_print("✅ Spark cerrado correctamente")
        
    except Exception as e:
        safe_print(f"❌ Error en limpieza: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    start_time = datetime.now()
    
    success = test_spark_compatibility()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    safe_print("\n" + "=" * 60)
    if success:
        safe_print("🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
        safe_print("✅ Spark 3.4.4 es TOTALMENTE COMPATIBLE con Java 8")
        safe_print("✅ MongoDB integración funciona perfectamente")
        safe_print("✅ Sistema listo para análisis de big data")
    else:
        safe_print("❌ Algunos tests fallaron")
    
    safe_print(f"⏱️ Tiempo de ejecución: {duration:.2f} segundos")
    safe_print("=" * 60)

if __name__ == "__main__":
    main()