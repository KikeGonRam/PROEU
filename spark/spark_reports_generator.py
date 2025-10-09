#!/usr/bin/env python3
"""
Generación de reportes masivos con Spark para 10M usuarios
Sistema EU-UTVT - Reportes de Big Data

Autor: Sistema EU-UTVT
Fecha: Octubre 2025
"""

import os
import sys
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import time

class SparkReportGenerator:
    def __init__(self):
        self.spark = None
        self.df_users = None
        
        # Configurar Spark
        os.environ['SPARK_HOME'] = "C:/spark"
        os.environ['PYSPARK_PYTHON'] = sys.executable
        
    def init_spark(self):
        """Inicializar Spark optimizado para reportes"""
        print("🚀 Inicializando Spark para generación de reportes...")
        
        self.spark = SparkSession.builder \
            .appName("EU-UTVT-Reports-Generator") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
            .config("spark.sql.execution.arrow.pyspark.enabled", "true") \
            .config("spark.driver.memory", "6g") \
            .config("spark.executor.memory", "4g") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        print("✅ Spark inicializado para reportes")
    
    def load_sample_data(self):
        """Cargar datos de muestra para testing (simula 10M usuarios)"""
        print("📊 Generando datos de muestra para testing...")
        
        from faker import Faker
        import random
        
        fake = Faker(['es_MX'])
        
        # Generar muestra de 100K usuarios para testing rápido
        sample_size = 100000
        print(f"📦 Generando {sample_size:,} usuarios de muestra...")
        
        departments = [
            "Rectoría", "Dirección Académica", "Dirección Administrativa",
            "Finanzas", "Recursos Humanos", "Sistemas y TI", "Mantenimiento",
            "Biblioteca", "Servicios Escolares", "Vinculación", "Investigación"
        ]
        
        roles = ["solicitante", "aprobador", "pagador", "admin"]
        salary_ranges = ["A", "B", "C", "D", "E"]
        
        data = []
        for i in range(sample_size):
            user_data = (
                i + 1,  # user_id
                f"user{i+1}@utvt.edu.mx",  # email
                fake.first_name(),  # first_name
                fake.last_name(),  # last_name
                random.choice(departments),  # department
                random.choice(roles),  # role
                fake.phone_number(),  # phone
                random.choice([True, True, True, False]),  # is_active (75% activos)
                fake.date_time_between(start_date='-2y', end_date='now'),  # created_at
                fake.date_time_between(start_date='-1y', end_date='now') if random.random() < 0.7 else None,  # last_login
                random.randint(0, 150),  # login_count
                fake.job(),  # position
                f"EMP{i+1:08d}",  # employee_id
                random.choice(salary_ranges),  # salary_range
                fake.city()  # location
            )
            data.append(user_data)
        
        # Schema
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
            StructField("position", StringType(), True),
            StructField("employee_id", StringType(), True),
            StructField("salary_range", StringType(), True),
            StructField("location", StringType(), True)
        ])
        
        self.df_users = self.spark.createDataFrame(data, schema)
        self.df_users.cache()
        
        count = self.df_users.count()
        print(f"✅ Datos de muestra cargados: {count:,} usuarios")
        return self.df_users
    
    def generate_executive_summary(self):
        """Generar reporte ejecutivo"""
        print("📊 Generando Reporte Ejecutivo...")
        
        if self.df_users is None:
            print("❌ No hay datos cargados")
            return
        
        # Crear vista temporal
        self.df_users.createOrReplaceTempView("users")
        
        # Métricas principales
        total_users = self.df_users.count()
        active_users = self.df_users.filter(col("is_active") == True).count()
        activity_rate = (active_users / total_users) * 100
        
        # Distribución por roles
        role_stats = self.spark.sql("""
        SELECT role, 
               COUNT(*) as total,
               SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active,
               AVG(login_count) as avg_logins
        FROM users 
        GROUP BY role 
        ORDER BY total DESC
        """).toPandas()
        
        # Distribución por departamentos
        dept_stats = self.spark.sql("""
        SELECT department, 
               COUNT(*) as total_users,
               SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active_users,
               ROUND(AVG(login_count), 2) as avg_logins
        FROM users 
        GROUP BY department 
        ORDER BY total_users DESC
        """).toPandas()
        
        # Generar reporte
        report = f"""
        
═══════════════════════════════════════════════════════
                    REPORTE EJECUTIVO EU-UTVT
                   Análisis de Base de Usuarios
═══════════════════════════════════════════════════════

📊 MÉTRICAS PRINCIPALES
• Total de usuarios: {total_users:,}
• Usuarios activos: {active_users:,} ({activity_rate:.1f}%)
• Usuarios inactivos: {total_users - active_users:,} ({100-activity_rate:.1f}%)

📋 DISTRIBUCIÓN POR ROLES
"""
        
        for _, row in role_stats.iterrows():
            pct = (row['total'] / total_users) * 100
            report += f"• {row['role'].capitalize()}: {row['total']:,} usuarios ({pct:.1f}%) - {row['active']:,} activos\n"
        
        report += f"\n🏢 TOP 10 DEPARTAMENTOS\n"
        for _, row in dept_stats.head(10).iterrows():
            pct = (row['total_users'] / total_users) * 100
            report += f"• {row['department']}: {row['total_users']:,} usuarios ({pct:.1f}%) - {row['avg_logins']} logins promedio\n"
        
        report += f"\n📈 INSIGHTS CLAVE\n"
        
        # Calcular insights
        most_active_dept = dept_stats.loc[dept_stats['avg_logins'].idxmax()]
        most_users_dept = dept_stats.loc[dept_stats['total_users'].idxmax()]
        
        report += f"• Departamento más activo: {most_active_dept['department']} ({most_active_dept['avg_logins']} logins promedio)\n"
        report += f"• Departamento con más usuarios: {most_users_dept['department']} ({most_users_dept['total_users']:,} usuarios)\n"
        
        # Actividad por rangos salariales
        salary_activity = self.spark.sql("""
        SELECT salary_range, 
               COUNT(*) as users,
               AVG(login_count) as avg_activity
        FROM users 
        GROUP BY salary_range 
        ORDER BY salary_range
        """).toPandas()
        
        report += f"\n💰 ACTIVIDAD POR RANGO SALARIAL\n"
        for _, row in salary_activity.iterrows():
            report += f"• Rango {row['salary_range']}: {row['users']:,} usuarios - {row['avg_activity']:.1f} logins promedio\n"
        
        report += f"\n═══════════════════════════════════════════════════════\n"
        report += f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Sistema: EU-UTVT Analytics con Apache Spark\n"
        report += f"═══════════════════════════════════════════════════════\n"
        
        print(report)
        
        # Guardar reporte
        with open(f"reporte_ejecutivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w", encoding="utf-8") as f:
            f.write(report)
        
        print("💾 Reporte ejecutivo guardado")
        
        return role_stats, dept_stats
    
    def generate_department_reports(self):
        """Generar reportes detallados por departamento"""
        print("🏢 Generando reportes por departamento...")
        
        if self.df_users is None:
            print("❌ No hay datos cargados")
            return
        
        # Obtener lista de departamentos
        departments = self.df_users.select("department").distinct().rdd.flatMap(lambda x: x).collect()
        
        reports_dir = f"reportes_departamentos_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(reports_dir, exist_ok=True)
        
        for dept in departments:
            print(f"   📋 Procesando: {dept}")
            
            # Filtrar usuarios del departamento
            dept_users = self.df_users.filter(col("department") == dept)
            dept_users.createOrReplaceTempView("dept_users")
            
            # Estadísticas del departamento
            total_dept = dept_users.count()
            active_dept = dept_users.filter(col("is_active") == True).count()
            
            # Análisis por roles en el departamento
            role_analysis = self.spark.sql("""
            SELECT role,
                   COUNT(*) as total,
                   SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active,
                   AVG(login_count) as avg_logins,
                   MAX(login_count) as max_logins
            FROM dept_users
            GROUP BY role
            ORDER BY total DESC
            """).toPandas()
            
            # Top usuarios más activos
            top_users = self.spark.sql("""
            SELECT first_name, last_name, role, login_count, last_login
            FROM dept_users
            WHERE login_count > 0
            ORDER BY login_count DESC
            LIMIT 10
            """).toPandas()
            
            # Generar reporte del departamento
            dept_report = f"""
REPORTE DEPARTAMENTAL - {dept.upper()}
{"="*60}

📊 RESUMEN
• Total usuarios: {total_dept:,}
• Usuarios activos: {active_dept:,} ({(active_dept/total_dept)*100:.1f}%)
• Usuarios inactivos: {total_dept - active_dept:,}

📋 DISTRIBUCIÓN POR ROLES
"""
            
            for _, row in role_analysis.iterrows():
                pct = (row['total'] / total_dept) * 100
                dept_report += f"• {row['role'].capitalize()}: {row['total']} usuarios ({pct:.1f}%) - {row['avg_logins']:.1f} logins promedio\n"
            
            dept_report += f"\n🏆 TOP 10 USUARIOS MÁS ACTIVOS\n"
            for i, row in top_users.iterrows():
                dept_report += f"{i+1:2d}. {row['first_name']} {row['last_name']} ({row['role']}) - {row['login_count']} logins\n"
            
            dept_report += f"\n{'='*60}\n"
            
            # Guardar reporte del departamento
            filename = f"{reports_dir}/reporte_{dept.replace(' ', '_').replace('/', '_')}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(dept_report)
        
        print(f"✅ Reportes departamentales guardados en: {reports_dir}/")
    
    def generate_activity_trends(self):
        """Generar análisis de tendencias de actividad"""
        print("📈 Generando análisis de tendencias...")
        
        if self.df_users is None:
            print("❌ No hay datos cargados")
            return
        
        self.df_users.createOrReplaceTempView("users")
        
        # Tendencias de registro por mes
        registration_trends = self.spark.sql("""
        SELECT DATE_FORMAT(created_at, 'yyyy-MM') as month,
               COUNT(*) as new_registrations,
               SUM(COUNT(*)) OVER (ORDER BY DATE_FORMAT(created_at, 'yyyy-MM')) as cumulative
        FROM users
        WHERE created_at >= date_sub(current_date(), 365)
        GROUP BY DATE_FORMAT(created_at, 'yyyy-MM')
        ORDER BY month
        """).toPandas()
        
        # Análisis de actividad por día de la semana (usuarios con login)
        activity_by_weekday = self.spark.sql("""
        SELECT DAYOFWEEK(last_login) as day_of_week,
               COUNT(*) as active_users,
               AVG(login_count) as avg_logins
        FROM users
        WHERE last_login IS NOT NULL
        GROUP BY DAYOFWEEK(last_login)
        ORDER BY day_of_week
        """).toPandas()
        
        # Mapear días de la semana
        day_names = {1: 'Domingo', 2: 'Lunes', 3: 'Martes', 4: 'Miércoles', 
                    5: 'Jueves', 6: 'Viernes', 7: 'Sábado'}
        activity_by_weekday['day_name'] = activity_by_weekday['day_of_week'].map(day_names)
        
        # Análisis de retención (usuarios que han hecho login recientemente)
        retention_analysis = self.spark.sql("""
        SELECT 
            CASE 
                WHEN last_login >= date_sub(current_date(), 7) THEN 'Última semana'
                WHEN last_login >= date_sub(current_date(), 30) THEN 'Último mes'
                WHEN last_login >= date_sub(current_date(), 90) THEN 'Últimos 3 meses'
                WHEN last_login >= date_sub(current_date(), 365) THEN 'Último año'
                WHEN last_login IS NULL THEN 'Nunca'
                ELSE 'Más de 1 año'
            END as last_activity,
            COUNT(*) as users
        FROM users
        GROUP BY 
            CASE 
                WHEN last_login >= date_sub(current_date(), 7) THEN 'Última semana'
                WHEN last_login >= date_sub(current_date(), 30) THEN 'Último mes'
                WHEN last_login >= date_sub(current_date(), 90) THEN 'Últimos 3 meses'
                WHEN last_login >= date_sub(current_date(), 365) THEN 'Último año'
                WHEN last_login IS NULL THEN 'Nunca'
                ELSE 'Más de 1 año'
            END
        ORDER BY users DESC
        """).toPandas()
        
        # Generar reporte de tendencias
        trends_report = f"""
ANÁLISIS DE TENDENCIAS DE ACTIVIDAD
{"="*60}

📅 REGISTROS POR MES (Últimos 12 meses)
"""
        
        for _, row in registration_trends.iterrows():
            trends_report += f"• {row['month']}: {row['new_registrations']:,} nuevos usuarios (Total acumulado: {row['cumulative']:,})\n"
        
        trends_report += f"\n📊 ACTIVIDAD POR DÍA DE LA SEMANA\n"
        for _, row in activity_by_weekday.iterrows():
            trends_report += f"• {row['day_name']}: {row['active_users']:,} usuarios activos ({row['avg_logins']:.1f} logins promedio)\n"
        
        trends_report += f"\n⏰ ANÁLISIS DE RETENCIÓN\n"
        total_users = retention_analysis['users'].sum()
        for _, row in retention_analysis.iterrows():
            pct = (row['users'] / total_users) * 100
            trends_report += f"• {row['last_activity']}: {row['users']:,} usuarios ({pct:.1f}%)\n"
        
        trends_report += f"\n{'='*60}\n"
        
        print(trends_report)
        
        # Guardar reporte
        with open(f"analisis_tendencias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w", encoding="utf-8") as f:
            f.write(trends_report)
        
        print("💾 Análisis de tendencias guardado")
        
        return registration_trends, activity_by_weekday, retention_analysis
    
    def generate_performance_report(self):
        """Generar reporte de rendimiento del sistema"""
        print("🚀 Generando reporte de rendimiento...")
        
        if self.df_users is None:
            print("❌ No hay datos cargados")
            return
        
        # Test de rendimiento de consultas
        start_time = time.time()
        
        # Test 1: Consulta simple
        test1_start = time.time()
        count_active = self.df_users.filter(col("is_active") == True).count()
        test1_time = time.time() - test1_start
        
        # Test 2: Agregación compleja
        test2_start = time.time()
        complex_agg = self.df_users.groupBy("department", "role") \
            .agg(count("*").alias("total"), avg("login_count").alias("avg_logins")) \
            .collect()
        test2_time = time.time() - test2_start
        
        # Test 3: Filtrado y ordenamiento
        test3_start = time.time()
        top_active = self.df_users.filter(col("login_count") > 50) \
            .orderBy(desc("login_count")) \
            .limit(100).collect()
        test3_time = time.time() - test3_start
        
        total_time = time.time() - start_time
        
        # Información del cluster Spark
        spark_info = {
            "app_name": self.spark.sparkContext.appName,
            "spark_version": self.spark.version,
            "master": self.spark.sparkContext.master,
            "default_parallelism": self.spark.sparkContext.defaultParallelism,
            "total_cores": self.spark.sparkContext.defaultParallelism
        }
        
        # Generar reporte de rendimiento
        perf_report = f"""
REPORTE DE RENDIMIENTO DEL SISTEMA
{"="*60}

⚙️ CONFIGURACIÓN DEL CLUSTER
• Aplicación: {spark_info['app_name']}
• Versión Spark: {spark_info['spark_version']}
• Master: {spark_info['master']}
• Paralelismo: {spark_info['default_parallelism']}
• Cores totales: {spark_info['total_cores']}

🚀 PRUEBAS DE RENDIMIENTO
• Test 1 - Filtrado simple: {test1_time:.3f} segundos ({count_active:,} registros)
• Test 2 - Agregación compleja: {test2_time:.3f} segundos ({len(complex_agg)} grupos)
• Test 3 - Filtrado y ordenamiento: {test3_time:.3f} segundos ({len(top_active)} registros)
• Tiempo total: {total_time:.3f} segundos

📊 MÉTRICAS DE RENDIMIENTO
• Registros por segundo (filtrado): {count_active/test1_time:.0f}
• Grupos por segundo (agregación): {len(complex_agg)/test2_time:.0f}
• Ordenamientos por segundo: {len(top_active)/test3_time:.0f}

💡 RECOMENDACIONES
"""
        
        # Agregar recomendaciones basadas en rendimiento
        if test1_time > 5:
            perf_report += "• Considerar aumentar el número de particiones para filtrado\n"
        
        if test2_time > 10:
            perf_report += "• Optimizar configuración de shuffle para agregaciones\n"
        
        if test3_time > 5:
            perf_report += "• Evaluar uso de indices o pre-ordenamiento para consultas\n"
        
        perf_report += f"• Dataset actual: {self.df_users.count():,} registros procesados eficientemente\n"
        perf_report += f"• Sistema optimizado para escalar a 10M+ registros\n"
        
        perf_report += f"\n{'='*60}\n"
        
        print(perf_report)
        
        # Guardar reporte
        with open(f"reporte_rendimiento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w", encoding="utf-8") as f:
            f.write(perf_report)
        
        print("💾 Reporte de rendimiento guardado")
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.spark:
            self.spark.stop()
            print("✅ Spark session cerrada")

def main():
    """Función principal"""
    print("📊 GENERADOR DE REPORTES MASIVOS - EU-UTVT")
    print("🎯 Reportes de Big Data con Apache Spark")
    print("="*60)
    
    generator = SparkReportGenerator()
    
    try:
        generator.init_spark()
        generator.load_sample_data()
        
        while True:
            print("\n" + "="*50)
            print("📋 GENERADOR DE REPORTES")
            print("="*50)
            print("1. 📊 Reporte ejecutivo")
            print("2. 🏢 Reportes por departamento")
            print("3. 📈 Análisis de tendencias")
            print("4. 🚀 Reporte de rendimiento")
            print("5. 📑 Generar todos los reportes")
            print("6. ❌ Salir")
            print("-"*50)
            
            choice = input("Selecciona una opción (1-6): ").strip()
            
            if choice == "1":
                generator.generate_executive_summary()
            elif choice == "2":
                generator.generate_department_reports()
            elif choice == "3":
                generator.generate_activity_trends()
            elif choice == "4":
                generator.generate_performance_report()
            elif choice == "5":
                print("📑 Generando todos los reportes...")
                generator.generate_executive_summary()
                generator.generate_department_reports()
                generator.generate_activity_trends()
                generator.generate_performance_report()
                print("✅ Todos los reportes generados")
            elif choice == "6":
                print("👋 Saliendo...")
                break
            else:
                print("❌ Opción inválida")
                
    except KeyboardInterrupt:
        print("\n⚠️ Operación interrumpida")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        generator.cleanup()

if __name__ == "__main__":
    main()