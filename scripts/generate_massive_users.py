#!/usr/bin/env python3
"""
Script para generar 10 millones de usuarios en la base de datos
Diseñado para pruebas de rendimiento y escalabilidad

Autor: Sistema EU-UTVT
Fecha: Octubre 2025
"""

import asyncio
import time
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict
import hashlib
from motor.motor_asyncio import AsyncIOMotorClient
from faker import Faker
import bcrypt
import sys
import os

# Configuración de MongoDB
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "eu_utvt_db"
COLLECTION_NAME = "users"

# Configuración del script
BATCH_SIZE = 1000  # Usuarios por lote
TOTAL_USERS = 10_000_000  # 10 millones
PROGRESS_INTERVAL = 50_000  # Mostrar progreso cada 50k usuarios

# Configurar Faker para datos realistas
fake = Faker(['es_MX', 'es_ES', 'en_US'])

class MassiveUserGenerator:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.start_time = None
        self.users_created = 0
        
        # Datos para generar usuarios variados
        self.departments = [
            "Rectoría", "Dirección Académica", "Dirección Administrativa",
            "Finanzas", "Recursos Humanos", "Sistemas y TI", "Mantenimiento",
            "Biblioteca", "Servicios Escolares", "Vinculación", "Investigación",
            "Desarrollo Académico", "Planeación", "Jurídico", "Comunicación",
            "Calidad", "Seguridad", "Compras", "Almacén", "Transporte"
        ]
        
        self.roles = [
            ("solicitante", 70),    # 70% solicitantes
            ("aprobador", 20),      # 20% aprobadores
            ("pagador", 8),         # 8% pagadores
            ("admin", 2)            # 2% administradores
        ]
        
        self.email_domains = [
            "utvt.edu.mx", "gmail.com", "hotmail.com", "outlook.com",
            "yahoo.com", "live.com", "icloud.com"
        ]
        
    async def connect_db(self):
        """Conectar a MongoDB"""
        print("🔌 Conectando a MongoDB...")
        try:
            self.client = AsyncIOMotorClient(MONGO_URI)
            self.db = self.client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]
            
            # Verificar conexión
            await self.client.admin.command('ping')
            print("✅ Conexión a MongoDB establecida")
            
            # Crear índices para optimizar búsquedas
            await self.create_indexes()
            
        except Exception as e:
            print(f"❌ Error conectando a MongoDB: {e}")
            sys.exit(1)
    
    async def create_indexes(self):
        """Crear índices para optimizar la base de datos"""
        print("📊 Creando índices de base de datos...")
        
        try:
            # Índice único en email
            await self.collection.create_index("email", unique=True)
            
            # Índices compuestos para búsquedas comunes
            await self.collection.create_index([("role", 1), ("department", 1)])
            await self.collection.create_index([("is_active", 1), ("role", 1)])
            await self.collection.create_index("created_at")
            await self.collection.create_index("last_login")
            
            print("✅ Índices creados correctamente")
            
        except Exception as e:
            print(f"⚠️ Warning creando índices: {e}")
    
    def generate_user_data(self, user_id: int) -> Dict:
        """Generar datos de un usuario"""
        
        # Seleccionar rol basado en distribución
        role = self.select_weighted_role()
        
        # Generar datos básicos
        first_name = fake.first_name()
        last_name = fake.last_name()
        
        # Email único usando ID para evitar duplicados
        email_domain = random.choice(self.email_domains)
        email = f"user{user_id}_{first_name.lower()}.{last_name.lower()}@{email_domain}"
        
        # Password hasheada (todos tendrán 'password123' por defecto para testing)
        password_hash = bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Fechas
        created_at = fake.date_time_between(start_date='-2y', end_date='now')
        last_login = None
        if random.random() < 0.7:  # 70% han hecho login alguna vez
            last_login = fake.date_time_between(start_date=created_at, end_date='now')
        
        return {
            "user_id": user_id,
            "email": email,
            "password": password_hash,
            "first_name": first_name,
            "last_name": last_name,
            "department": random.choice(self.departments),
            "role": role,
            "phone": self.generate_phone(),
            "is_active": random.choice([True, True, True, False]),  # 75% activos
            "created_at": created_at,
            "last_login": last_login,
            "login_count": random.randint(0, 100) if last_login else 0,
            "profile": {
                "position": fake.job(),
                "employee_id": f"EMP{user_id:08d}",
                "hire_date": fake.date_between(start_date='-5y', end_date='-1m'),
                "salary_range": random.choice(["A", "B", "C", "D", "E"]),
                "location": fake.city(),
                "manager_id": None  # Se podría asignar después
            },
            "preferences": {
                "language": random.choice(["es", "en"]),
                "timezone": "America/Mexico_City",
                "notifications": {
                    "email": random.choice([True, False]),
                    "sms": random.choice([True, False]),
                    "push": random.choice([True, False])
                },
                "theme": random.choice(["light", "dark", "auto"])
            },
            "metadata": {
                "source": "massive_generation",
                "version": "1.0",
                "generated_at": datetime.utcnow(),
                "batch_id": user_id // BATCH_SIZE
            }
        }
    
    def select_weighted_role(self) -> str:
        """Seleccionar rol basado en distribución de pesos"""
        rand = random.randint(1, 100)
        cumulative = 0
        
        for role, weight in self.roles:
            cumulative += weight
            if rand <= cumulative:
                return role
        
        return "solicitante"  # fallback
    
    def generate_phone(self) -> str:
        """Generar número de teléfono mexicano"""
        area_codes = ["55", "722", "777", "33", "81", "228", "662", "998"]
        area = random.choice(area_codes)
        number = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        return f"+52 {area} {number[:3]} {number[3:]}"
    
    async def insert_batch(self, users_batch: List[Dict]) -> bool:
        """Insertar un lote de usuarios"""
        try:
            await self.collection.insert_many(users_batch, ordered=False)
            return True
        except Exception as e:
            print(f"⚠️ Error insertando lote: {e}")
            return False
    
    async def generate_users_batch(self, start_id: int, batch_size: int) -> List[Dict]:
        """Generar un lote de usuarios"""
        users = []
        for i in range(batch_size):
            user_id = start_id + i
            user_data = self.generate_user_data(user_id)
            users.append(user_data)
        
        return users
    
    def print_progress(self, current: int, total: int, elapsed_time: float):
        """Mostrar progreso de generación"""
        percentage = (current / total) * 100
        rate = current / elapsed_time if elapsed_time > 0 else 0
        eta = (total - current) / rate if rate > 0 else 0
        
        print(f"📈 Progreso: {current:,}/{total:,} ({percentage:.1f}%) | "
              f"Velocidad: {rate:.0f} usuarios/seg | "
              f"ETA: {eta/60:.1f} min")
    
    async def generate_massive_users(self):
        """Función principal para generar usuarios masivamente"""
        print("🚀 Iniciando generación masiva de usuarios...")
        print(f"📊 Total a generar: {TOTAL_USERS:,} usuarios")
        print(f"📦 Tamaño de lote: {BATCH_SIZE:,} usuarios")
        print(f"⏱️ Progreso cada: {PROGRESS_INTERVAL:,} usuarios")
        print("-" * 60)
        
        self.start_time = time.time()
        
        # Verificar si ya existen usuarios
        existing_count = await self.collection.count_documents({})
        if existing_count > 0:
            print(f"⚠️ Ya existen {existing_count:,} usuarios en la base de datos")
            response = input("¿Continuar agregando más usuarios? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operación cancelada")
                return
        
        # Generar usuarios en lotes
        for batch_start in range(1, TOTAL_USERS + 1, BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE - 1, TOTAL_USERS)
            actual_batch_size = batch_end - batch_start + 1
            
            # Generar lote de usuarios
            users_batch = await self.generate_users_batch(batch_start, actual_batch_size)
            
            # Insertar en base de datos
            success = await self.insert_batch(users_batch)
            
            if success:
                self.users_created += actual_batch_size
                
                # Mostrar progreso
                if self.users_created % PROGRESS_INTERVAL == 0 or self.users_created == TOTAL_USERS:
                    elapsed = time.time() - self.start_time
                    self.print_progress(self.users_created, TOTAL_USERS, elapsed)
            else:
                print(f"❌ Error en lote {batch_start}-{batch_end}")
        
        # Estadísticas finales
        await self.print_final_stats()
    
    async def print_final_stats(self):
        """Mostrar estadísticas finales"""
        total_time = time.time() - self.start_time
        
        print("\n" + "="*60)
        print("📊 GENERACIÓN COMPLETADA")
        print("="*60)
        print(f"✅ Usuarios creados: {self.users_created:,}")
        print(f"⏱️ Tiempo total: {total_time/60:.2f} minutos ({total_time:.2f} segundos)")
        print(f"🚀 Velocidad promedio: {self.users_created/total_time:.2f} usuarios/segundo")
        
        # Verificar en base de datos
        total_in_db = await self.collection.count_documents({})
        print(f"🗃️ Total en BD: {total_in_db:,}")
        
        # Estadísticas por rol
        print("\n📈 Distribución por roles:")
        for role, _ in self.roles:
            count = await self.collection.count_documents({"role": role})
            percentage = (count / total_in_db) * 100 if total_in_db > 0 else 0
            print(f"   {role.capitalize()}: {count:,} ({percentage:.1f}%)")
        
        # Estadísticas por departamento
        print(f"\n🏢 Departamentos creados: {len(self.departments)}")
        
        # Tamaño estimado
        print(f"\n💾 Tamaño estimado de datos: ~{(total_in_db * 2) / 1024:.1f} MB")
        
        print("="*60)
    
    async def cleanup(self):
        """Limpiar conexiones"""
        if self.client:
            self.client.close()
            print("🔌 Conexión cerrada")

async def main():
    """Función principal"""
    print("🎯 GENERADOR MASIVO DE USUARIOS - EU-UTVT")
    print("="*60)
    
    generator = MassiveUserGenerator()
    
    try:
        # Conectar a base de datos
        await generator.connect_db()
        
        # Confirmar operación
        print(f"\n⚠️  ADVERTENCIA: Se van a generar {TOTAL_USERS:,} usuarios")
        print("   Esto puede tomar varios minutos y usar considerable espacio en disco.")
        response = input("\n¿Continuar? (y/N): ")
        
        if response.lower() != 'y':
            print("❌ Operación cancelada")
            return
        
        # Generar usuarios
        await generator.generate_users_batch()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Operación interrumpida por el usuario")
        print(f"✅ Usuarios creados hasta ahora: {generator.users_created:,}")
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        
    finally:
        await generator.cleanup()

# Script adicional para verificar los datos
async def verify_data():
    """Verificar los datos generados"""
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    
    try:
        print("🔍 Verificando datos generados...")
        
        # Conteos básicos
        total = await collection.count_documents({})
        active = await collection.count_documents({"is_active": True})
        
        print(f"👥 Total usuarios: {total:,}")
        print(f"✅ Usuarios activos: {active:,}")
        print(f"❌ Usuarios inactivos: {total - active:,}")
        
        # Muestreo de datos
        sample = await collection.find().limit(5).to_list(length=5)
        print(f"\n📝 Muestra de datos (primeros 5 usuarios):")
        for user in sample:
            print(f"   {user['first_name']} {user['last_name']} - {user['email']} ({user['role']})")
            
    except Exception as e:
        print(f"❌ Error verificando datos: {e}")
        
    finally:
        client.close()

if __name__ == "__main__":
    # Verificar dependencias
    try:
        import motor
        import faker
        import bcrypt
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        print("📦 Instala con: pip install motor faker bcrypt")
        sys.exit(1)
    
    # Ejecutar generación
    asyncio.run(main())
    
    # Opción para verificar datos
    verify = input("\n🔍 ¿Verificar datos generados? (y/N): ")
    if verify.lower() == 'y':
        asyncio.run(verify_data())
    
    print("\n🎉 Script completado!")