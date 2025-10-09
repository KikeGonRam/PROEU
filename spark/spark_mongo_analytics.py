#!/usr/bin/env python3
"""
Integración Spark + MongoDB para análisis masivo de 10M usuarios
Sistema EU-UTVT con Apache Spark 3.4.4 + Java 8

Autor: Sistema EU-UTVT  
Fecha: Octubre 2025
Versión: 3.4.4 Compatible con Java 8
"""

import os
import sys
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pymongo
from pymongo import MongoClient
import time

# Configuración
SPARK_HOME = "C:/spark"
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "eu_utvt_db"
COLLECTION_NAME = "users"

class SparkMongoAnalyzer:
    def __init__(self):
        self.spark = None
        self.mongo_client = None
        self.df_users = None
        
        # Configurar variables de entorno para Spark
        os.environ['SPARK_HOME'] = SPARK_HOME
        os.environ['PYSPARK_PYTHON'] = sys.executable
        
    def init_spark(self):
        """Inicializar Spark 3.4.4 con configuración optimizada para Java 8"""
        print("🚀 Inicializando Apache Spark 3.4.4...")
        
        try:
            self.spark = SparkSession.builder \
                .appName("EU-UTVT-BigData-Analytics-3.4.4") \
                .config("spark.sql.adaptive.enabled", "true") \
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
                .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
                .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
                .config("spark.sql.adaptive.skewJoin.enabled", "true") \
                .config("spark.default.parallelism", "8") \
                .config("spark.sql.adaptive.coalescePartitions.initialPartitionNum", "200") \
                .config("spark.driver.memory", "4g") \
                .config("spark.executor.memory", "4g") \
                .config("spark.driver.maxResultSize", "2g") \
                .config("spark.sql.shuffle.partitions", "200") \
                .config("spark.sql.codegen.wholeStage", "true") \
                .getOrCreate()
            
            # Configurar nivel de log
            self.spark.sparkContext.setLogLevel("WARN")
            
            print("✅ Spark 3.4.4 inicializado correctamente")
            print(f"📊 Spark Version: {self.spark.version}")
            print(f"🖥️ Spark Master: {self.spark.sparkContext.master}")
            print(f"⚙️ Particiones por defecto: {self.spark.sparkContext.defaultParallelism}")
            print(f"☕ Java Version Compatible: 8+")
            
        except Exception as e:
            print(f"❌ Error inicializando Spark: {e}")
            sys.exit(1)
    
    def connect_mongo(self):
        """Conectar a MongoDB"""
        print("🔗 Conectando a MongoDB...")
        try:
            self.mongo_client = MongoClient(MONGO_URI)
            # Verificar conexión
            self.mongo_client.admin.command('ping')
            print("✅ Conexión a MongoDB establecida")
        except Exception as e:
            print(f"❌ Error conectando a MongoDB: {e}")
            sys.exit(1)
    
    def load_users_to_spark(self):
        """Cargar usuarios de MongoDB a Spark DataFrame"""
        print("📊 Cargando usuarios de MongoDB a Spark...")
        start_time = time.time()
        
        try:
            # Obtener datos de MongoDB
            db = self.mongo_client[DATABASE_NAME]
            collection = db[COLLECTION_NAME]
            
            # Contar documentos
            total_docs = collection.count_documents({})
            print(f"📈 Total usuarios en MongoDB: {total_docs:,}")
            
            if total_docs == 0:
                print("⚠️ No hay usuarios en la base de datos")
                return None
            
            # Obtener datos por lotes para evitar problemas de memoria
            print("⚡ Cargando datos en lotes...")
            
            # Definir esquema para optimizar carga
            schema = StructType([
                StructField("user_id", IntegerType(), True),
                StructField("email", StringType(), True),
                StructField("first_name", StringType(), True),
                StructField("last_name", StringType(), True),
                StructField("department", StringType(), True),
                StructField("role", StringType(), True),
                StructField("phone", StringType(), True),
                StructField("is_active", BooleanType(), True),
                StructField("created_at", TimestampType(), True),
                StructField("last_login", TimestampType(), True),
                StructField("login_count", IntegerType(), True),
                StructField("profile", StructType([
                    StructField("position", StringType(), True),
                    StructField("employee_id", StringType(), True),
                    StructField("salary_range", StringType(), True),
                    StructField("location", StringType(), True)
                ]), True)
            ])
            
            # Convertir documentos MongoDB a lista de filas
            batch_size = 50000  # Procesar en lotes de 50K
            all_rows = []
            processed = 0
            
            cursor = collection.find({}, {
                "_id": 0,  # Excluir _id de MongoDB
                "user_id": 1,
                "email": 1,
                "first_name": 1,
                "last_name": 1,
                "department": 1,
                "role": 1,
                "phone": 1,
                "is_active": 1,
                "created_at": 1,
                "last_login": 1,
                "login_count": 1,
                "profile.position": 1,
                "profile.employee_id": 1,
                "profile.salary_range": 1,
                "profile.location": 1
            }).batch_size(batch_size)
            
            for doc in cursor:
                # Convertir documento a fila de Spark
                profile = doc.get('profile', {})
                row_data = (
                    doc.get('user_id'),
                    doc.get('email'),
                    doc.get('first_name'),
                    doc.get('last_name'),
                    doc.get('department'),
                    doc.get('role'),
                    doc.get('phone'),
                    doc.get('is_active'),
                    doc.get('created_at'),
                    doc.get('last_login'),
                    doc.get('login_count', 0),
                    (
                        profile.get('position'),
                        profile.get('employee_id'),
                        profile.get('salary_range'),
                        profile.get('location')
                    )
                )
                all_rows.append(row_data)
                processed += 1
                
                if processed % batch_size == 0:
                    print(f"   📦 Procesados: {processed:,}/{total_docs:,} usuarios")
            
            # Crear DataFrame de Spark
            print("🔄 Creando Spark DataFrame...")
            self.df_users = self.spark.createDataFrame(all_rows, schema)
            
            # Cachear DataFrame para consultas rápidas
            self.df_users.cache()
            
            # Trigger acción para materializeor
            count = self.df_users.count()
            
            load_time = time.time() - start_time
            print(f"✅ Datos cargados en Spark: {count:,} usuarios")
            print(f"⏱️ Tiempo de carga: {load_time:.2f} segundos")
            print(f"🚀 Velocidad: {count/load_time:.0f} registros/segundo")
            
            return self.df_users
            
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            return None
    
    def basic_analytics(self):
        """Realizar análisis básico de los datos"""
        if self.df_users is None:
            print("❌ No hay datos cargados")
            return
        
        print("\n" + "="*60)
        print("📊 ANÁLISIS BÁSICO DE 10M USUARIOS")
        print("="*60)
        
        # Estadísticas básicas
        total_users = self.df_users.count()
        print(f"👥 Total usuarios: {total_users:,}")
        
        # Usuarios activos vs inactivos
        active_users = self.df_users.filter(col("is_active") == True).count()
        inactive_users = total_users - active_users
        print(f"✅ Usuarios activos: {active_users:,} ({(active_users/total_users)*100:.1f}%)")
        print(f"❌ Usuarios inactivos: {inactive_users:,} ({(inactive_users/total_users)*100:.1f}%)")
        
        # Distribución por roles
        print(f"\n📋 Distribución por roles:")
        role_dist = self.df_users.groupBy("role").count().orderBy(desc("count"))
        role_dist.show()
        
        # Distribución por departamentos (Top 10)
        print(f"🏢 Top 10 departamentos:")
        dept_dist = self.df_users.groupBy("department").count().orderBy(desc("count")).limit(10)
        dept_dist.show()
        
        # Estadísticas de login
        users_with_login = self.df_users.filter(col("last_login").isNotNull()).count()
        print(f"📱 Usuarios que han hecho login: {users_with_login:,}")
        
        # Promedio de logins
        avg_logins = self.df_users.agg(avg("login_count")).collect()[0][0]
        print(f"📈 Promedio de logins por usuario: {avg_logins:.2f}")
        
    def advanced_analytics(self):
        """Análisis avanzado con Spark SQL"""
        if self.df_users is None:
            print("❌ No hay datos cargados")
            return
        
        print("\n" + "="*60)
        print("🔬 ANÁLISIS AVANZADO CON SPARK SQL")
        print("="*60)
        
        # Crear vista temporal para SQL
        self.df_users.createOrReplaceTempView("users")
        
        # 1. Análisis de actividad por departamento y rol
        print("📊 Actividad por departamento y rol:")
        activity_query = """
        SELECT department, role, 
               COUNT(*) as total_users,
               SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active_users,
               AVG(login_count) as avg_logins,
               ROUND((SUM(CASE WHEN is_active THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as activity_rate
        FROM users 
        GROUP BY department, role
        ORDER BY total_users DESC
        LIMIT 20
        """
        self.spark.sql(activity_query).show(20, truncate=False)
        
        # 2. Análisis temporal de registros
        print("\n📅 Registros por mes (últimos 12 meses):")
        temporal_query = """
        SELECT DATE_FORMAT(created_at, 'yyyy-MM') as month,
               COUNT(*) as new_users,
               SUM(COUNT(*)) OVER (ORDER BY DATE_FORMAT(created_at, 'yyyy-MM')) as cumulative_users
        FROM users 
        WHERE created_at >= date_sub(current_date(), 365)
        GROUP BY DATE_FORMAT(created_at, 'yyyy-MM')
        ORDER BY month
        """
        self.spark.sql(temporal_query).show()
        
        # 3. Usuarios más activos por departamento
        print("\n🏆 Top usuarios por logins por departamento:")
        top_users_query = """
        SELECT department, first_name, last_name, email, login_count,
               ROW_NUMBER() OVER (PARTITION BY department ORDER BY login_count DESC) as rank
        FROM users 
        WHERE login_count > 0
        """
        top_users_df = self.spark.sql(top_users_query)
        top_users_df.filter(col("rank") <= 3).show(30, truncate=False)
        
        # 4. Análisis de dominios de email
        print("\n📧 Dominios de email más comunes:")
        email_domains_query = """
        SELECT SUBSTRING_INDEX(email, '@', -1) as domain,
               COUNT(*) as user_count,
               ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM users)), 2) as percentage
        FROM users
        GROUP BY SUBSTRING_INDEX(email, '@', -1)
        ORDER BY user_count DESC
        LIMIT 10
        """
        self.spark.sql(email_domains_query).show()
        
    def performance_tests(self):
        """Pruebas de rendimiento con Spark"""
        if self.df_users is None:
            print("❌ No hay datos cargados")
            return
        
        print("\n" + "="*60)
        print("🚀 PRUEBAS DE RENDIMIENTO SPARK")
        print("="*60)
        
        # Test 1: Filtrado masivo
        print("🔍 Test 1: Filtrado de usuarios activos por departamento")
        start_time = time.time()
        filtered_df = self.df_users.filter(
            (col("is_active") == True) & 
            (col("department").isin(["Sistemas y TI", "Finanzas", "Recursos Humanos"]))
        )
        result_count = filtered_df.count()
        test1_time = time.time() - start_time
        print(f"   Resultados: {result_count:,} usuarios")
        print(f"   Tiempo: {test1_time:.3f} segundos")
        
        # Test 2: Agregación compleja
        print("\n📊 Test 2: Agregación por múltiples dimensiones")
        start_time = time.time()
        agg_df = self.df_users.groupBy("department", "role", "is_active") \
            .agg(
                count("*").alias("total_users"),
                avg("login_count").alias("avg_logins"),
                max("login_count").alias("max_logins"),
                min("created_at").alias("earliest_user"),
                max("created_at").alias("latest_user")
            ).orderBy(desc("total_users"))
        
        agg_result = agg_df.collect()
        test2_time = time.time() - start_time
        print(f"   Grupos creados: {len(agg_result)}")
        print(f"   Tiempo: {test2_time:.3f} segundos")
        
        # Test 3: Join simulado (auto-join para testing)
        print("\n🔄 Test 3: Auto-join para testing de rendimiento")
        start_time = time.time()
        df_alias = self.df_users.alias("a")
        df_managers = self.df_users.filter(col("role") == "aprobador").alias("b")
        
        join_df = df_alias.join(
            df_managers,
            col("a.department") == col("b.department"),
            "inner"
        ).select(
            col("a.user_id").alias("employee_id"),
            col("a.first_name").alias("employee_name"),
            col("b.user_id").alias("manager_id"),
            col("b.first_name").alias("manager_name"),
            col("a.department")
        )
        
        join_count = join_df.count()
        test3_time = time.time() - start_time
        print(f"   Relaciones creadas: {join_count:,}")
        print(f"   Tiempo: {test3_time:.3f} segundos")
        
        # Resumen de rendimiento
        print(f"\n📈 Resumen de rendimiento:")
        print(f"   🔍 Filtrado: {test1_time:.3f}s")
        print(f"   📊 Agregación: {test2_time:.3f}s") 
        print(f"   🔄 Join: {test3_time:.3f}s")
        
    def export_analysis_results(self):
        """Exportar resultados de análisis"""
        if self.df_users is None:
            print("❌ No hay datos cargados")
            return
        
        print("\n💾 Exportando resultados de análisis...")
        
        try:
            # Crear directorio de resultados
            results_dir = "spark_analysis_results"
            os.makedirs(results_dir, exist_ok=True)
            
            # Exportar distribución por roles
            role_dist = self.df_users.groupBy("role").count().orderBy(desc("count"))
            role_dist.coalesce(1).write.mode("overwrite").option("header", "true").csv(f"{results_dir}/role_distribution")
            
            # Exportar distribución por departamentos
            dept_dist = self.df_users.groupBy("department").count().orderBy(desc("count"))
            dept_dist.coalesce(1).write.mode("overwrite").option("header", "true").csv(f"{results_dir}/department_distribution")
            
            # Exportar estadísticas por departamento y rol
            stats_df = self.df_users.groupBy("department", "role") \
                .agg(
                    count("*").alias("total_users"),
                    sum(when(col("is_active"), 1).otherwise(0)).alias("active_users"),
                    avg("login_count").alias("avg_logins")
                )
            stats_df.coalesce(1).write.mode("overwrite").option("header", "true").csv(f"{results_dir}/detailed_statistics")
            
            print(f"✅ Resultados exportados a: {results_dir}/")
            
        except Exception as e:
            print(f"❌ Error exportando: {e}")
    
    def cleanup(self):
        """Limpiar recursos"""
        print("\n🧹 Limpiando recursos...")
        
        if self.spark:
            self.spark.stop()
            print("✅ Spark session cerrada")
        
        if self.mongo_client:
            self.mongo_client.close()
            print("✅ MongoDB connection cerrada")

def main():
    """Función principal"""
    print("🌟 SPARK + MONGODB ANALYTICS - EU-UTVT")
    print("🎯 Análisis de 10 Millones de Usuarios")
    print("="*60)
    
    analyzer = SparkMongoAnalyzer()
    
    try:
        # Inicializar componentes
        analyzer.init_spark()
        analyzer.connect_mongo()
        
        # Cargar datos
        df = analyzer.load_users_to_spark()
        if df is None:
            print("❌ No se pudieron cargar los datos")
            return
        
        # Menú de análisis
        while True:
            print("\n" + "="*50)
            print("📊 MENÚ DE ANÁLISIS SPARK")
            print("="*50)
            print("1. 📈 Análisis básico")
            print("2. 🔬 Análisis avanzado (Spark SQL)")
            print("3. 🚀 Pruebas de rendimiento")
            print("4. 💾 Exportar resultados")
            print("5. 🔄 Recargar datos")
            print("6. ❌ Salir")
            print("-"*50)
            
            choice = input("Selecciona una opción (1-6): ").strip()
            
            if choice == "1":
                analyzer.basic_analytics()
            elif choice == "2":
                analyzer.advanced_analytics()
            elif choice == "3":
                analyzer.performance_tests()
            elif choice == "4":
                analyzer.export_analysis_results()
            elif choice == "5":
                analyzer.load_users_to_spark()
            elif choice == "6":
                print("👋 Saliendo...")
                break
            else:
                print("❌ Opción inválida")
                
    except KeyboardInterrupt:
        print("\n⚠️ Operación interrumpida")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    finally:
        analyzer.cleanup()

if __name__ == "__main__":
    main()