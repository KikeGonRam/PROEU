#!/usr/bin/env python3
"""
Análisis MongoDB con PySpark Local (Compatible Java 8)
Sistema EU-UTVT - Análisis de usuarios sin cluster Spark

Autor: Sistema EU-UTVT
Fecha: Octubre 2025
"""

import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pymongo import MongoClient
import sys
import os

# Configuración
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "eu_utvt_db"
COLLECTION_NAME = "users"

class MongoAnalyzer:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.collection = None
        self.df_users = None
        
    def connect_mongo(self):
        """Conectar a MongoDB"""
        print("🔗 Conectando a MongoDB...")
        try:
            self.mongo_client = MongoClient(MONGO_URI)
            # Verificar conexión
            self.mongo_client.admin.command('ping')
            self.db = self.mongo_client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]
            print("✅ Conexión a MongoDB establecida")
        except Exception as e:
            print(f"❌ Error conectando a MongoDB: {e}")
            sys.exit(1)
    
    def load_users_to_pandas(self, limit=None):
        """Cargar usuarios de MongoDB a Pandas DataFrame"""
        print("📊 Cargando usuarios de MongoDB...")
        start_time = time.time()
        
        try:
            # Contar documentos
            total_docs = self.collection.count_documents({})
            print(f"📈 Total usuarios en MongoDB: {total_docs:,}")
            
            if total_docs == 0:
                print("⚠️ No hay usuarios en la base de datos")
                return None
            
            # Determinar límite de carga
            load_limit = min(limit or total_docs, total_docs)
            if limit and limit < total_docs:
                print(f"📦 Cargando muestra de {load_limit:,} usuarios para análisis rápido")
            else:
                print(f"📦 Cargando todos los {load_limit:,} usuarios")
            
            # Proyección optimizada
            projection = {
                "_id": 0,
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
            }
            
            # Obtener datos
            cursor = self.collection.find({}, projection).limit(load_limit)
            
            # Convertir a lista
            data = []
            processed = 0
            batch_size = 10000
            
            for doc in cursor:
                profile = doc.get('profile', {})
                
                # Aplanar estructura
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
                
                if processed % batch_size == 0:
                    print(f"   📦 Procesados: {processed:,}/{load_limit:,} usuarios")
            
            # Crear DataFrame de Pandas
            print("🔄 Creando Pandas DataFrame...")
            self.df_users = pd.DataFrame(data)
            
            # Convertir tipos de datos
            if not self.df_users.empty:
                # Convertir fechas
                if 'created_at' in self.df_users.columns:
                    self.df_users['created_at'] = pd.to_datetime(self.df_users['created_at'])
                if 'last_login' in self.df_users.columns:
                    self.df_users['last_login'] = pd.to_datetime(self.df_users['last_login'])
                
                # Convertir boolean
                if 'is_active' in self.df_users.columns:
                    self.df_users['is_active'] = self.df_users['is_active'].astype(bool)
                
                # Convertir numéricos
                if 'login_count' in self.df_users.columns:
                    self.df_users['login_count'] = pd.to_numeric(self.df_users['login_count'], errors='coerce').fillna(0)
            
            load_time = time.time() - start_time
            count = len(self.df_users)
            print(f"✅ Datos cargados: {count:,} usuarios")
            print(f"⏱️ Tiempo de carga: {load_time:.2f} segundos")
            print(f"🚀 Velocidad: {count/load_time:.0f} registros/segundo")
            
            return self.df_users
            
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
            return None
    
    def basic_analytics(self):
        """Realizar análisis básico de los datos"""
        if self.df_users is None or self.df_users.empty:
            print("❌ No hay datos cargados")
            return
        
        print("\n" + "="*60)
        print("📊 ANÁLISIS BÁSICO DE USUARIOS")
        print("="*60)
        
        # Estadísticas básicas
        total_users = len(self.df_users)
        print(f"👥 Total usuarios analizados: {total_users:,}")
        
        # Usuarios activos vs inactivos
        active_users = self.df_users['is_active'].sum()
        inactive_users = total_users - active_users
        print(f"✅ Usuarios activos: {active_users:,} ({(active_users/total_users)*100:.1f}%)")
        print(f"❌ Usuarios inactivos: {inactive_users:,} ({(inactive_users/total_users)*100:.1f}%)")
        
        # Distribución por roles
        print(f"\n📋 Distribución por roles:")
        role_dist = self.df_users['role'].value_counts()
        for role, count in role_dist.items():
            percentage = (count / total_users) * 100
            print(f"   {role.capitalize()}: {count:,} ({percentage:.1f}%)")
        
        # Distribución por departamentos (Top 10)
        print(f"\n🏢 Top 10 departamentos:")
        dept_dist = self.df_users['department'].value_counts().head(10)
        for dept, count in dept_dist.items():
            percentage = (count / total_users) * 100
            print(f"   {dept}: {count:,} ({percentage:.1f}%)")
        
        # Estadísticas de login
        users_with_login = self.df_users['last_login'].notna().sum()
        print(f"\n📱 Usuarios que han hecho login: {users_with_login:,}")
        
        # Promedio de logins
        avg_logins = self.df_users['login_count'].mean()
        max_logins = self.df_users['login_count'].max()
        print(f"📈 Promedio de logins: {avg_logins:.2f}")
        print(f"🏆 Máximo logins: {max_logins:,}")
        
        # Estadísticas por rango salarial
        if 'salary_range' in self.df_users.columns:
            print(f"\n💰 Distribución por rango salarial:")
            salary_dist = self.df_users['salary_range'].value_counts().sort_index()
            for salary, count in salary_dist.items():
                if pd.notna(salary):
                    percentage = (count / total_users) * 100
                    print(f"   Rango {salary}: {count:,} ({percentage:.1f}%)")
    
    def advanced_analytics(self):
        """Análisis avanzado con Pandas"""
        if self.df_users is None or self.df_users.empty:
            print("❌ No hay datos cargados")
            return
        
        print("\n" + "="*60)
        print("🔬 ANÁLISIS AVANZADO")
        print("="*60)
        
        # 1. Análisis cruzado departamento-rol
        print("📊 Análisis por departamento y rol:")
        cross_analysis = self.df_users.groupby(['department', 'role']).agg({
            'user_id': 'count',
            'is_active': 'sum',
            'login_count': 'mean'
        }).round(2)
        cross_analysis.columns = ['total_users', 'active_users', 'avg_logins']
        cross_analysis['activity_rate'] = (cross_analysis['active_users'] / cross_analysis['total_users'] * 100).round(2)
        
        # Mostrar top 20
        top_combinations = cross_analysis.sort_values('total_users', ascending=False).head(20)
        print(top_combinations.to_string())
        
        # 2. Análisis temporal (si hay fechas)
        if 'created_at' in self.df_users.columns and self.df_users['created_at'].notna().any():
            print("\n📅 Análisis temporal de registros:")
            
            # Registros por mes (últimos 12 meses)
            recent_date = self.df_users['created_at'].max()
            year_ago = recent_date - timedelta(days=365)
            recent_users = self.df_users[self.df_users['created_at'] >= year_ago]
            
            if not recent_users.empty:
                monthly_registrations = recent_users.groupby(recent_users['created_at'].dt.to_period('M')).size()
                print("Registros por mes (últimos 12 meses):")
                for month, count in monthly_registrations.items():
                    print(f"   {month}: {count:,} nuevos usuarios")
        
        # 3. Top usuarios más activos
        print("\n🏆 Top 10 usuarios más activos:")
        top_active = self.df_users.nlargest(10, 'login_count')[
            ['first_name', 'last_name', 'department', 'role', 'login_count']
        ]
        for idx, user in top_active.iterrows():
            print(f"   {user['first_name']} {user['last_name']} ({user['department']}) - {user['role']} - {user['login_count']} logins")
        
        # 4. Análisis de dominios de email
        if 'email' in self.df_users.columns:
            print("\n📧 Dominios de email más comunes:")
            email_domains = self.df_users['email'].str.split('@').str[1].value_counts().head(10)
            total_emails = len(self.df_users)
            for domain, count in email_domains.items():
                percentage = (count / total_emails) * 100
                print(f"   {domain}: {count:,} ({percentage:.1f}%)")
    
    def performance_tests(self):
        """Pruebas de rendimiento con Pandas"""
        if self.df_users is None or self.df_users.empty:
            print("❌ No hay datos cargados")
            return
        
        print("\n" + "="*60)
        print("🚀 PRUEBAS DE RENDIMIENTO")
        print("="*60)
        
        # Test 1: Filtrado masivo
        print("🔍 Test 1: Filtrado de usuarios activos por departamentos específicos")
        start_time = time.time()
        target_depts = ["Sistemas y TI", "Finanzas", "Recursos Humanos"]
        filtered_df = self.df_users[
            (self.df_users['is_active'] == True) & 
            (self.df_users['department'].isin(target_depts))
        ]
        result_count = len(filtered_df)
        test1_time = time.time() - start_time
        print(f"   Resultados: {result_count:,} usuarios")
        print(f"   Tiempo: {test1_time:.3f} segundos")
        
        # Test 2: Agregación compleja
        print("\n📊 Test 2: Agregación por múltiples dimensiones")
        start_time = time.time()
        agg_result = self.df_users.groupby(['department', 'role', 'is_active']).agg({
            'user_id': 'count',
            'login_count': ['mean', 'max', 'min'],
            'created_at': ['min', 'max']
        })
        test2_time = time.time() - start_time
        print(f"   Grupos creados: {len(agg_result)}")
        print(f"   Tiempo: {test2_time:.3f} segundos")
        
        # Test 3: Ordenamiento masivo
        print("\n🔄 Test 3: Ordenamiento por múltiples campos")
        start_time = time.time()
        sorted_df = self.df_users.sort_values(['department', 'role', 'login_count'], ascending=[True, True, False])
        test3_time = time.time() - start_time
        print(f"   Registros ordenados: {len(sorted_df):,}")
        print(f"   Tiempo: {test3_time:.3f} segundos")
        
        # Test 4: Búsqueda de patrones
        print("\n🔎 Test 4: Búsqueda de patrones en emails")
        start_time = time.time()
        utvt_emails = self.df_users[self.df_users['email'].str.contains('utvt.edu.mx', na=False)]
        test4_time = time.time() - start_time
        print(f"   Emails UTVT encontrados: {len(utvt_emails):,}")
        print(f"   Tiempo: {test4_time:.3f} segundos")
        
        # Resumen de rendimiento
        total_records = len(self.df_users)
        print(f"\n📈 Resumen de rendimiento ({total_records:,} registros):")
        print(f"   🔍 Filtrado: {test1_time:.3f}s ({result_count/test1_time:.0f} registros/s)")
        print(f"   📊 Agregación: {test2_time:.3f}s")
        print(f"   🔄 Ordenamiento: {test3_time:.3f}s ({total_records/test3_time:.0f} registros/s)")
        print(f"   🔎 Búsqueda: {test4_time:.3f}s ({total_records/test4_time:.0f} registros/s)")
    
    def export_results(self):
        """Exportar resultados de análisis"""
        if self.df_users is None or self.df_users.empty:
            print("❌ No hay datos cargados")
            return
        
        print("\n💾 Exportando resultados...")
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Exportar distribución por roles
            role_dist = self.df_users['role'].value_counts().to_frame('count')
            role_dist.to_csv(f'role_distribution_{timestamp}.csv')
            
            # Exportar distribución por departamentos
            dept_dist = self.df_users['department'].value_counts().to_frame('count')
            dept_dist.to_csv(f'department_distribution_{timestamp}.csv')
            
            # Exportar estadísticas detalladas
            detailed_stats = self.df_users.groupby(['department', 'role']).agg({
                'user_id': 'count',
                'is_active': 'sum',
                'login_count': 'mean'
            }).round(2)
            detailed_stats.to_csv(f'detailed_statistics_{timestamp}.csv')
            
            # Exportar muestra de datos
            sample_data = self.df_users.head(1000)
            sample_data.to_csv(f'sample_data_{timestamp}.csv', index=False)
            
            print(f"✅ Resultados exportados con timestamp: {timestamp}")
            print(f"   📊 role_distribution_{timestamp}.csv")
            print(f"   🏢 department_distribution_{timestamp}.csv")
            print(f"   📈 detailed_statistics_{timestamp}.csv")
            print(f"   📋 sample_data_{timestamp}.csv")
            
        except Exception as e:
            print(f"❌ Error exportando: {e}")
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.mongo_client:
            self.mongo_client.close()
            print("✅ MongoDB connection cerrada")

def main():
    """Función principal"""
    print("🌟 MONGODB ANALYTICS - EU-UTVT")
    print("🎯 Análisis de Usuarios (Compatible Java 8)")
    print("="*60)
    
    analyzer = MongoAnalyzer()
    
    try:
        # Conectar a MongoDB
        analyzer.connect_mongo()
        
        # Preguntar sobre el tamaño de muestra
        print("\n📊 Opciones de carga de datos:")
        print("1. 🚀 Muestra rápida (100K usuarios) - Recomendado")
        print("2. 📊 Muestra media (500K usuarios)")
        print("3. 💾 Todos los usuarios (puede ser lento)")
        
        choice = input("\nSelecciona opción (1-3): ").strip()
        
        if choice == "1":
            limit = 100000
        elif choice == "2":
            limit = 500000
        else:
            limit = None
        
        # Cargar datos
        df = analyzer.load_users_to_pandas(limit)
        if df is None or df.empty:
            print("❌ No se pudieron cargar los datos")
            return
        
        # Menú de análisis
        while True:
            print("\n" + "="*50)
            print("📊 MENÚ DE ANÁLISIS")
            print("="*50)
            print("1. 📈 Análisis básico")
            print("2. 🔬 Análisis avanzado")
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
                analyzer.export_results()
            elif choice == "5":
                print("\n🔄 Recargando datos...")
                df = analyzer.load_users_to_pandas(limit)
                if df is None:
                    print("❌ Error recargando datos")
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