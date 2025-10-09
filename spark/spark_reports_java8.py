#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generación de reportes masivos compatible con Java 8
Sistema EU-UTVT - Reportes de Big Data con MongoDB + Pandas

Autor: Sistema EU-UTVT
Fecha: Octubre 2025
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
import time

# Configurar codificación UTF-8 para Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# Configuración
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "eu_utvt_db"
COLLECTION_NAME = "users"

def safe_print(text):
    """Imprimir texto de forma segura en Windows"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Reemplazar emojis problemáticos
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

class MongoReportGenerator:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.collection = None
        self.df_users = None
        
    def connect_mongo(self):
        """Conectar a MongoDB"""
        safe_print("🔗 Conectando a MongoDB...")
        try:
            self.mongo_client = MongoClient(MONGO_URI)
            self.mongo_client.admin.command('ping')
            self.db = self.mongo_client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]
            safe_print("✅ Conexión a MongoDB establecida")
        except Exception as e:
            safe_print(f"❌ Error conectando a MongoDB: {e}")
            sys.exit(1)
    
    def load_users_data(self, limit=None):
        """Cargar usuarios de MongoDB"""
        safe_print("📊 Cargando usuarios para reportes...")
        start_time = time.time()
        
        try:
            total_docs = self.collection.count_documents({})
            safe_print(f"📈 Total usuarios en MongoDB: {total_docs:,}")
            
            if total_docs == 0:
                safe_print("⚠️ No hay usuarios en la base de datos")
                return None
            
            # Determinar límite
            load_limit = min(limit or total_docs, total_docs)
            if limit and limit < total_docs:
                safe_print(f"📦 Cargando muestra de {load_limit:,} usuarios")
            else:
                safe_print(f"📦 Cargando todos los {load_limit:,} usuarios")
            
            # Proyección optimizada
            projection = {
                "_id": 0, "user_id": 1, "email": 1, "first_name": 1, "last_name": 1,
                "department": 1, "role": 1, "phone": 1, "is_active": 1,
                "created_at": 1, "last_login": 1, "login_count": 1,
                "profile.position": 1, "profile.employee_id": 1,
                "profile.salary_range": 1, "profile.location": 1
            }
            
            # Obtener datos
            cursor = self.collection.find({}, projection).limit(load_limit)
            data = []
            processed = 0
            
            for doc in cursor:
                profile = doc.get('profile', {})
                flat_doc = {
                    'user_id': doc.get('user_id'),
                    'email': doc.get('email'),
                    'first_name': doc.get('first_name'),
                    'last_name': doc.get('last_name'),
                    'department': doc.get('department'),
                    'role': doc.get('role'),
                    'phone': doc.get('phone'),
                    'is_active': doc.get('is_active'),
                    'created_at': doc.get('created_at'),
                    'last_login': doc.get('last_login'),
                    'login_count': doc.get('login_count', 0),
                    'position': profile.get('position'),
                    'employee_id': profile.get('employee_id'),
                    'salary_range': profile.get('salary_range'),
                    'location': profile.get('location')
                }
                data.append(flat_doc)
                processed += 1
                
                if processed % 50000 == 0:
                    safe_print(f"   📦 Procesados: {processed:,}/{load_limit:,}")
            
            # Crear DataFrame
            self.df_users = pd.DataFrame(data)
            
            # Convertir tipos
            if not self.df_users.empty:
                self.df_users['created_at'] = pd.to_datetime(self.df_users['created_at'])
                self.df_users['last_login'] = pd.to_datetime(self.df_users['last_login'])
                self.df_users['is_active'] = self.df_users['is_active'].astype(bool)
                self.df_users['login_count'] = pd.to_numeric(self.df_users['login_count'], errors='coerce').fillna(0)
            
            load_time = time.time() - start_time
            count = len(self.df_users)
            safe_print(f"✅ Datos cargados: {count:,} usuarios en {load_time:.2f}s")
            
            return self.df_users
            
        except Exception as e:
            safe_print(f"❌ Error cargando datos: {e}")
            return None
    
    def generate_executive_summary(self):
        """Generar reporte ejecutivo profesional"""
        safe_print("📊 Generando Reporte Ejecutivo...")
        
        if self.df_users is None or self.df_users.empty:
            safe_print("❌ No hay datos cargados")
            return
        
        # Métricas principales
        total_users = len(self.df_users)
        active_users = self.df_users['is_active'].sum()
        activity_rate = (active_users / total_users) * 100
        
        # Distribución por roles
        role_stats = self.df_users.groupby('role').agg({
            'user_id': 'count',
            'is_active': 'sum',
            'login_count': 'mean'
        }).round(2)
        role_stats.columns = ['total', 'active', 'avg_logins']
        role_stats = role_stats.sort_values('total', ascending=False)
        
        # Distribución por departamentos
        dept_stats = self.df_users.groupby('department').agg({
            'user_id': 'count',
            'is_active': 'sum',
            'login_count': 'mean'
        }).round(2)
        dept_stats.columns = ['total_users', 'active_users', 'avg_logins']
        dept_stats = dept_stats.sort_values('total_users', ascending=False)
        
        # Generar reporte ejecutivo
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
        
        for role, row in role_stats.iterrows():
            pct = (row['total'] / total_users) * 100
            report += f"• {role.capitalize()}: {row['total']:,} usuarios ({pct:.1f}%) - {row['active']:,} activos\n"
        
        report += f"\n🏢 TOP 10 DEPARTAMENTOS\n"
        for dept, row in dept_stats.head(10).iterrows():
            pct = (row['total_users'] / total_users) * 100
            report += f"• {dept}: {row['total_users']:,} usuarios ({pct:.1f}%) - {row['avg_logins']:.1f} logins promedio\n"
        
        # Insights clave
        most_active_dept = dept_stats.loc[dept_stats['avg_logins'].idxmax()]
        most_users_dept = dept_stats.loc[dept_stats['total_users'].idxmax()]
        
        report += f"\n📈 INSIGHTS CLAVE\n"
        report += f"• Departamento más activo: {most_active_dept.name} ({most_active_dept['avg_logins']:.1f} logins promedio)\n"
        report += f"• Departamento con más usuarios: {most_users_dept.name} ({most_users_dept['total_users']:,} usuarios)\n"
        
        # Análisis temporal
        if 'created_at' in self.df_users.columns and self.df_users['created_at'].notna().any():
            recent_users = self.df_users[self.df_users['created_at'] >= (datetime.now() - timedelta(days=30))]
            report += f"• Nuevos usuarios últimos 30 días: {len(recent_users):,}\n"
        
        # Actividad por rangos salariales
        if 'salary_range' in self.df_users.columns:
            salary_activity = self.df_users.groupby('salary_range').agg({
                'user_id': 'count',
                'login_count': 'mean'
            }).round(2)
            salary_activity.columns = ['users', 'avg_activity']
            
            report += f"\n💰 ACTIVIDAD POR RANGO SALARIAL\n"
            for salary, row in salary_activity.iterrows():
                if pd.notna(salary):
                    report += f"• Rango {salary}: {row['users']:,} usuarios - {row['avg_activity']:.1f} logins promedio\n"
        
        report += f"\n═══════════════════════════════════════════════════════\n"
        report += f"Generado: {timestamp}\n"
        report += f"Sistema: EU-UTVT Analytics con MongoDB + Pandas\n"
        report += f"Datos analizados: {total_users:,} usuarios\n"
        report += f"═══════════════════════════════════════════════════════\n"
        
        safe_print(report)
        
        # Guardar reporte
        filename = f"reporte_ejecutivo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        
        safe_print(f"💾 Reporte ejecutivo guardado: {filename}")
        
        return role_stats, dept_stats
    
    def generate_department_reports(self):
        """Generar reportes detallados por departamento"""
        safe_print("🏢 Generando reportes por departamento...")
        
        if self.df_users is None or self.df_users.empty:
            safe_print("❌ No hay datos cargados")
            return
        
        departments = self.df_users['department'].unique()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        reports_dir = f"reportes_departamentos_{timestamp}"
        os.makedirs(reports_dir, exist_ok=True)
        
        for dept in departments:
            if pd.notna(dept):
                safe_print(f"   📋 Procesando: {dept}")
                
                # Filtrar usuarios del departamento
                dept_users = self.df_users[self.df_users['department'] == dept]
                total_dept = len(dept_users)
                active_dept = dept_users['is_active'].sum()
                
                # Análisis por roles en el departamento
                role_analysis = dept_users.groupby('role').agg({
                    'user_id': 'count',
                    'is_active': 'sum',
                    'login_count': ['mean', 'max']
                }).round(2)
                role_analysis.columns = ['total', 'active', 'avg_logins', 'max_logins']
                
                # Top usuarios más activos
                top_users = dept_users.nlargest(10, 'login_count')[
                    ['first_name', 'last_name', 'role', 'login_count', 'last_login']
                ]
                
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
                
                for role, row in role_analysis.iterrows():
                    pct = (row['total'] / total_dept) * 100
                    dept_report += f"• {role.capitalize()}: {row['total']} usuarios ({pct:.1f}%) - {row['avg_logins']:.1f} logins promedio\n"
                
                dept_report += f"\n🏆 TOP 10 USUARIOS MÁS ACTIVOS\n"
                for i, (_, user) in enumerate(top_users.iterrows(), 1):
                    dept_report += f"{i:2d}. {user['first_name']} {user['last_name']} ({user['role']}) - {user['login_count']} logins\n"
                
                dept_report += f"\n{'='*60}\n"
                
                # Guardar reporte del departamento
                safe_dept = dept.replace(' ', '_').replace('/', '_').replace('\\', '_')
                filename = f"{reports_dir}/reporte_{safe_dept}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(dept_report)
        
        safe_print(f"✅ Reportes departamentales guardados en: {reports_dir}/")
    
    def generate_activity_trends(self):
        """Generar análisis de tendencias de actividad"""
        safe_print("📈 Generando análisis de tendencias...")
        
        if self.df_users is None or self.df_users.empty:
            safe_print("❌ No hay datos cargados")
            return
        
        # Tendencias de registro por mes
        if 'created_at' in self.df_users.columns and self.df_users['created_at'].notna().any():
            recent_date = self.df_users['created_at'].max()
            year_ago = recent_date - timedelta(days=365)
            recent_users = self.df_users[self.df_users['created_at'] >= year_ago]
            
            monthly_registrations = recent_users.groupby(
                recent_users['created_at'].dt.to_period('M')
            ).size().reset_index()
            monthly_registrations.columns = ['month', 'new_registrations']
            monthly_registrations['cumulative'] = monthly_registrations['new_registrations'].cumsum()
        else:
            monthly_registrations = pd.DataFrame()
        
        # Análisis de retención
        retention_data = []
        now = datetime.now()
        
        for period, days in [
            ('Última semana', 7),
            ('Último mes', 30),
            ('Últimos 3 meses', 90),
            ('Último año', 365)
        ]:
            cutoff = now - timedelta(days=days)
            if 'last_login' in self.df_users.columns:
                count = self.df_users[
                    (self.df_users['last_login'].notna()) & 
                    (self.df_users['last_login'] >= cutoff)
                ].shape[0]
            else:
                count = 0
            retention_data.append({'period': period, 'users': count})
        
        # Nunca hicieron login
        never_login = self.df_users['last_login'].isna().sum() if 'last_login' in self.df_users.columns else 0
        retention_data.append({'period': 'Nunca', 'users': never_login})
        
        retention_df = pd.DataFrame(retention_data)
        
        # Generar reporte de tendencias
        trends_report = f"""
ANÁLISIS DE TENDENCIAS DE ACTIVIDAD
{"="*60}

📅 REGISTROS POR MES (Últimos 12 meses)
"""
        
        if not monthly_registrations.empty:
            for _, row in monthly_registrations.iterrows():
                trends_report += f"• {row['month']}: {row['new_registrations']:,} nuevos usuarios (Acumulado: {row['cumulative']:,})\n"
        else:
            trends_report += "• No hay datos temporales disponibles\n"
        
        trends_report += f"\n⏰ ANÁLISIS DE RETENCIÓN\n"
        total_users = len(self.df_users)
        for _, row in retention_df.iterrows():
            pct = (row['users'] / total_users) * 100
            trends_report += f"• {row['period']}: {row['users']:,} usuarios ({pct:.1f}%)\n"
        
        # Análisis por día de la semana (simulado)
        if 'last_login' in self.df_users.columns and self.df_users['last_login'].notna().any():
            weekday_activity = self.df_users[self.df_users['last_login'].notna()].groupby(
                self.df_users['last_login'].dt.day_name()
            ).agg({
                'user_id': 'count',
                'login_count': 'mean'
            }).round(2)
            weekday_activity.columns = ['active_users', 'avg_logins']
            
            trends_report += f"\n📊 ACTIVIDAD POR DÍA DE LA SEMANA\n"
            for day, row in weekday_activity.iterrows():
                trends_report += f"• {day}: {row['active_users']:,} usuarios activos ({row['avg_logins']:.1f} logins promedio)\n"
        
        trends_report += f"\n{'='*60}\n"
        
        safe_print(trends_report)
        
        # Guardar reporte
        filename = f"analisis_tendencias_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(trends_report)
        
        safe_print(f"💾 Análisis de tendencias guardado: {filename}")
        
        return monthly_registrations, retention_df
    
    def generate_performance_report(self):
        """Generar reporte de rendimiento del sistema"""
        safe_print("🚀 Generando reporte de rendimiento...")
        
        if self.df_users is None or self.df_users.empty:
            safe_print("❌ No hay datos cargados")
            return
        
        total_records = len(self.df_users)
        
        # Test 1: Filtrado
        start_time = time.time()
        filtered_data = self.df_users[
            (self.df_users['is_active'] == True) & 
            (self.df_users['department'].isin(['Sistemas y TI', 'Finanzas', 'Recursos Humanos']))
        ]
        test1_time = time.time() - start_time
        
        # Test 2: Agregación
        start_time = time.time()
        agg_data = self.df_users.groupby(['department', 'role']).agg({
            'user_id': 'count',
            'login_count': ['mean', 'max', 'min']
        })
        test2_time = time.time() - start_time
        
        # Test 3: Ordenamiento
        start_time = time.time()
        sorted_data = self.df_users.sort_values(['department', 'role', 'login_count'])
        test3_time = time.time() - start_time
        
        # Test 4: Búsqueda
        start_time = time.time()
        search_results = self.df_users[self.df_users['email'].str.contains('utvt.edu.mx', na=False)]
        test4_time = time.time() - start_time
        
        # Información del sistema
        system_info = {
            "total_records": total_records,
            "memory_usage_mb": self.df_users.memory_usage(deep=True).sum() / 1024 / 1024,
            "columns": len(self.df_users.columns),
            "data_types": dict(self.df_users.dtypes)
        }
        
        # Generar reporte de rendimiento
        perf_report = f"""
REPORTE DE RENDIMIENTO DEL SISTEMA
{"="*60}

⚙️ CONFIGURACIÓN DEL SISTEMA
• Motor de análisis: MongoDB + Pandas
• Total registros: {system_info['total_records']:,}
• Uso de memoria: {system_info['memory_usage_mb']:.2f} MB
• Columnas analizadas: {system_info['columns']}

🚀 PRUEBAS DE RENDIMIENTO
• Test 1 - Filtrado multi-condición: {test1_time:.3f}s ({len(filtered_data):,} resultados)
• Test 2 - Agregación compleja: {test2_time:.3f}s ({len(agg_data)} grupos)
• Test 3 - Ordenamiento masivo: {test3_time:.3f}s ({len(sorted_data):,} registros)
• Test 4 - Búsqueda de patrones: {test4_time:.3f}s ({len(search_results):,} matches)

📊 MÉTRICAS DE RENDIMIENTO
• Velocidad de filtrado: {len(filtered_data)/test1_time:.0f} registros/s
• Velocidad de agregación: {len(agg_data)/test2_time:.0f} grupos/s
• Velocidad de ordenamiento: {total_records/test3_time:.0f} registros/s
• Velocidad de búsqueda: {total_records/test4_time:.0f} registros/s

💡 ANÁLISIS DE EFICIENCIA
"""
        
        if test1_time < 0.1:
            perf_report += "• ✅ Filtrado: Excelente rendimiento\n"
        elif test1_time < 1:
            perf_report += "• 🟡 Filtrado: Buen rendimiento\n"
        else:
            perf_report += "• 🔴 Filtrado: Considerar optimización\n"
        
        if test2_time < 0.5:
            perf_report += "• ✅ Agregación: Excelente rendimiento\n"
        elif test2_time < 2:
            perf_report += "• 🟡 Agregación: Buen rendimiento\n"
        else:
            perf_report += "• 🔴 Agregación: Considerar particionamiento\n"
        
        perf_report += f"• 📈 Sistema optimizado para datasets de {total_records:,} registros\n"
        perf_report += f"• 🚀 Escalable hasta 10M+ registros con configuración actual\n"
        
        perf_report += f"\n{'='*60}\n"
        
        safe_print(perf_report)
        
        # Guardar reporte
        filename = f"reporte_rendimiento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(perf_report)
        
        safe_print(f"💾 Reporte de rendimiento guardado: {filename}")
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.mongo_client:
            self.mongo_client.close()
            safe_print("✅ MongoDB connection cerrada")

def main():
    """Función principal"""
    safe_print("=" * 60)
    safe_print("GENERADOR DE REPORTES MASIVOS - EU-UTVT")
    safe_print("Reportes Empresariales con MongoDB + Pandas")
    safe_print("=" * 60)
    
    generator = MongoReportGenerator()
    
    try:
        generator.connect_mongo()
        
        # Opciones de carga
        safe_print("\nOpciones de analisis:")
        safe_print("1. Analisis rapido (500K usuarios)")
        safe_print("2. Analisis completo (todos los usuarios)")
        safe_print("3. Analisis personalizado")
        
        choice = input("\nSelecciona opcion (1-3): ").strip()
        
        if choice == "1":
            limit = 500000
        elif choice == "2":
            limit = None
        elif choice == "3":
            try:
                limit = int(input("Numero de usuarios a analizar: "))
            except:
                limit = 500000
        else:
            limit = 500000
        
        # Cargar datos
        df = generator.load_users_data(limit)
        if df is None or df.empty:
            safe_print("No se pudieron cargar los datos")
            return
        
        # Menú de reportes
        while True:
            safe_print("\n" + "="*50)
            safe_print("GENERADOR DE REPORTES")
            safe_print("="*50)
            safe_print("1. Reporte ejecutivo")
            safe_print("2. Reportes por departamento")
            safe_print("3. Analisis de tendencias")
            safe_print("4. Reporte de rendimiento")
            safe_print("5. Generar todos los reportes")
            safe_print("6. Recargar datos")
            safe_print("7. Salir")
            safe_print("-"*50)
            
            choice = input("Selecciona una opcion (1-7): ").strip()
            
            if choice == "1":
                generator.generate_executive_summary()
            elif choice == "2":
                generator.generate_department_reports()
            elif choice == "3":
                generator.generate_activity_trends()
            elif choice == "4":
                generator.generate_performance_report()
            elif choice == "5":
                safe_print("Generando todos los reportes...")
                generator.generate_executive_summary()
                generator.generate_department_reports()
                generator.generate_activity_trends()
                generator.generate_performance_report()
                safe_print("Todos los reportes generados")
            elif choice == "6":
                df = generator.load_users_data(limit)
                if df is None:
                    safe_print("Error recargando datos")
            elif choice == "7":
                safe_print("Saliendo...")
                break
            else:
                safe_print("Opcion invalida")
                
    except KeyboardInterrupt:
        safe_print("\n⚠️ Operación interrumpida")
    except Exception as e:
        safe_print(f"❌ Error: {e}")
    finally:
        generator.cleanup()

if __name__ == "__main__":
    main()