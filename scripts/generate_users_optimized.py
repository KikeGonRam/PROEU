#!/usr/bin/env python3
"""
Script optimizado para generar 10 millones de usuarios de forma rápida
Versión optimizada con multiprocesamiento y mejores técnicas de inserción

Autor: Sistema EU-UTVT
Fecha: Octubre 2025
"""

import asyncio
import time
import random
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import hashlib
from motor.motor_asyncio import AsyncIOMotorClient
from faker import Faker
import bcrypt
import sys
import os
import json

# Configuración optimizada
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "eu_utvt_db"
COLLECTION_NAME = "users"

# Configuración de rendimiento
BATCH_SIZE = 5000      # Lotes más grandes para mejor rendimiento
TOTAL_USERS = 10_000_000
PROGRESS_INTERVAL = 100_000
CPU_CORES = mp.cpu_count()
MAX_WORKERS = min(CPU_CORES, 8)  # Máximo 8 workers

print(f"🖥️ CPU cores detectados: {CPU_CORES}")
print(f"👷 Workers a usar: {MAX_WORKERS}")

class OptimizedUserGenerator:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.start_time = None
        self.users_created = 0
        
        # Pre-computar datos para acelerar generación
        self.departments = [
            "Rectoría", "Dirección Académica", "Dirección Administrativa",
            "Finanzas", "Recursos Humanos", "Sistemas y TI", "Mantenimiento",
            "Biblioteca", "Servicios Escolares", "Vinculación", "Investigación",
            "Desarrollo Académico", "Planeación", "Jurídico", "Comunicación",
            "Calidad", "Seguridad", "Compras", "Almacén", "Transporte"
        ]
        
        self.roles_distribution = [
            ("solicitante", 7000),  # 70%
            ("aprobador", 2000),    # 20%
            ("pagador", 800),       # 8%
            ("admin", 200)          # 2%
        ]
        
        self.email_domains = [
            "utvt.edu.mx", "gmail.com", "hotmail.com", "outlook.com",
            "yahoo.com", "live.com", "icloud.com"
        ]
        
        # Pre-generar algunos datos comunes
        self.common_passwords = [
            bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            for _ in range(10)  # 10 passwords pre-hasheados
        ]
        
    async def connect_db(self):
        """Conectar a MongoDB con configuración optimizada"""
        print("🔌 Conectando a MongoDB con configuración optimizada...")
        
        try:
            # Configuración optimizada para inserciones masivas
            self.client = AsyncIOMotorClient(
                MONGO_URI,
                maxPoolSize=50,  # Pool de conexiones más grande
                serverSelectionTimeoutMS=5000,
                socketTimeoutMS=30000,
                connectTimeoutMS=5000,
                retryWrites=True
            )
            
            self.db = self.client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]
            
            # Verificar conexión
            await self.client.admin.command('ping')
            print("✅ Conexión optimizada establecida")
            
            # Configurar para inserciones masivas
            await self.optimize_database()
            
        except Exception as e:
            print(f"❌ Error conectando: {e}")
            sys.exit(1)
    
    async def optimize_database(self):
        """Optimizar configuración de base de datos para inserciones masivas"""
        print("⚡ Optimizando base de datos para inserciones masivas...")
        
        try:
            # Desactivar validación temporal para mayor velocidad
            await self.db.command({
                "collMod": COLLECTION_NAME,
                "validator": {},
                "validationLevel": "off"
            })
            
            # Solo crear índice esencial durante inserción
            await self.collection.drop_indexes()
            
            print("✅ Base de datos optimizada")
            
        except Exception as e:
            print(f"⚠️ Warning optimizando BD: {e}")
    
    async def create_final_indexes(self):
        """Crear índices al final del proceso"""
        print("📊 Creando índices finales...")
        
        try:
            # Crear índices en paralelo usando createIndexes
            index_specs = [
                {"key": {"email": 1}, "unique": True, "name": "email_unique"},
                {"key": {"role": 1, "department": 1}, "name": "role_dept"},
                {"key": {"is_active": 1, "role": 1}, "name": "active_role"},
                {"key": {"created_at": 1}, "name": "created_at"},
                {"key": {"user_id": 1}, "unique": True, "name": "user_id_unique"}
            ]
            
            await self.collection.create_indexes([
                {"key": spec["key"], **{k: v for k, v in spec.items() if k != "key"}}
                for spec in index_specs
            ])
            
            print("✅ Índices creados")
            
        except Exception as e:
            print(f"⚠️ Warning creando índices: {e}")
    
    async def insert_batch_optimized(self, users_batch: List[Dict]) -> bool:
        """Inserción optimizada de lotes"""
        try:
            # Usar insert_many con ordered=False para mejor rendimiento
            result = await self.collection.insert_many(
                users_batch, 
                ordered=False,
                bypass_document_validation=True  # Saltar validación para velocidad
            )
            return len(result.inserted_ids) == len(users_batch)
            
        except Exception as e:
            # Intentar inserción uno por uno si falla el lote
            success_count = 0
            for user in users_batch:
                try:
                    await self.collection.insert_one(user)
                    success_count += 1
                except:
                    continue
            
            return success_count > 0
    
    async def generate_users_parallel(self):
        """Generar usuarios usando multiprocesamiento"""
        print("🚀 Iniciando generación paralela de usuarios...")
        print(f"📊 Total: {TOTAL_USERS:,} | Lotes: {BATCH_SIZE:,} | Workers: {MAX_WORKERS}")
        print("-" * 70)
        
        self.start_time = time.time()
        
        # Calcular rangos para cada worker
        total_batches = (TOTAL_USERS + BATCH_SIZE - 1) // BATCH_SIZE
        batches_per_worker = total_batches // MAX_WORKERS
        
        # Crear tareas para workers
        tasks = []
        current_start = 1
        
        for worker_id in range(MAX_WORKERS):
            # Calcular rango para este worker
            start_batch = worker_id * batches_per_worker
            end_batch = min((worker_id + 1) * batches_per_worker, total_batches)
            
            if worker_id == MAX_WORKERS - 1:  # Último worker toma el resto
                end_batch = total_batches
            
            start_user_id = start_batch * BATCH_SIZE + 1
            end_user_id = min(end_batch * BATCH_SIZE, TOTAL_USERS)
            
            if start_user_id <= TOTAL_USERS:
                task = self.process_user_range(worker_id, start_user_id, end_user_id)
                tasks.append(task)
        
        # Ejecutar todas las tareas en paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Procesar resultados
        total_created = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Worker {i} falló: {result}")
            else:
                total_created += result
                print(f"✅ Worker {i} completado: {result:,} usuarios")
        
        self.users_created = total_created
        await self.print_final_stats()
    
    async def process_user_range(self, worker_id: int, start_id: int, end_id: int) -> int:
        """Procesar un rango de usuarios (ejecutado por un worker)"""
        created_count = 0
        current_id = start_id
        
        print(f"👷 Worker {worker_id}: procesando IDs {start_id:,} - {end_id:,}")
        
        while current_id <= end_id:
            batch_end = min(current_id + BATCH_SIZE - 1, end_id)
            batch_size = batch_end - current_id + 1
            
            # Generar lote de usuarios
            users_batch = await self.generate_batch_data(current_id, batch_size)
            
            # Insertar en BD
            if await self.insert_batch_optimized(users_batch):
                created_count += batch_size
                
                # Progreso por worker
                if created_count % (PROGRESS_INTERVAL // MAX_WORKERS) == 0:
                    elapsed = time.time() - self.start_time
                    rate = created_count / elapsed if elapsed > 0 else 0
                    print(f"📈 Worker {worker_id}: {created_count:,} usuarios | {rate:.0f}/seg")
            
            current_id = batch_end + 1
        
        return created_count
    
    async def generate_batch_data(self, start_id: int, batch_size: int) -> List[Dict]:
        """Generar datos de lote optimizado"""
        users = []
        
        # Usar loop executor para generación intensiva de datos
        loop = asyncio.get_event_loop()
        users = await loop.run_in_executor(
            None, 
            self.generate_users_sync, 
            start_id, 
            batch_size
        )
        
        return users
    
    def generate_users_sync(self, start_id: int, batch_size: int) -> List[Dict]:
        """Generación síncrona optimizada (para executor)"""
        fake = Faker(['es_MX'])  # Una instancia por worker
        users = []
        
        for i in range(batch_size):
            user_id = start_id + i
            
            # Datos optimizados
            first_name = fake.first_name()
            last_name = fake.last_name()
            
            # Email único simple
            domain = random.choice(self.email_domains)
            email = f"user{user_id}@{domain}"
            
            # Password pre-hasheado
            password = random.choice(self.common_passwords)
            
            # Rol basado en distribución
            role = self.select_role_fast(user_id)
            
            # Fechas simples
            created_at = fake.date_time_between(start_date='-1y', end_date='now')
            
            user_data = {
                "user_id": user_id,
                "email": email,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                "department": random.choice(self.departments),
                "role": role,
                "phone": f"+52 {random.randint(100,999)} {random.randint(100,999)} {random.randint(1000,9999)}",
                "is_active": True,  # Todos activos para simplificar
                "created_at": created_at,
                "last_login": None,
                "profile": {
                    "employee_id": f"EMP{user_id:08d}",
                    "position": fake.job()
                },
                "metadata": {
                    "generated_at": datetime.utcnow(),
                    "batch_id": user_id // BATCH_SIZE
                }
            }
            
            users.append(user_data)
        
        return users
    
    def select_role_fast(self, user_id: int) -> str:
        """Selección rápida de rol basada en ID"""
        # Distribución determinística basada en ID
        mod = user_id % 10000
        
        if mod < 7000:
            return "solicitante"
        elif mod < 9000:
            return "aprobador"
        elif mod < 9800:
            return "pagador"
        else:
            return "admin"
    
    async def print_final_stats(self):
        """Estadísticas finales optimizadas"""
        total_time = time.time() - self.start_time
        
        print("\n" + "="*70)
        print("🏁 GENERACIÓN MASIVA COMPLETADA")
        print("="*70)
        print(f"✅ Usuarios generados: {self.users_created:,}")
        print(f"⏱️ Tiempo total: {total_time/60:.2f} minutos")
        print(f"🚀 Velocidad: {self.users_created/total_time:.0f} usuarios/segundo")
        print(f"👷 Workers utilizados: {MAX_WORKERS}")
        
        # Verificar en BD
        total_in_db = await self.collection.count_documents({})
        print(f"🗃️ Verificado en BD: {total_in_db:,}")
        
        # Crear índices finales
        await self.create_final_indexes()
        
        print("="*70)
    
    async def cleanup(self):
        """Cleanup optimizado"""
        if self.client:
            self.client.close()

async def quick_verify():
    """Verificación rápida de datos"""
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    
    try:
        total = await collection.count_documents({})
        print(f"🔍 Total en BD: {total:,}")
        
        # Distribución por roles
        for role in ["solicitante", "aprobador", "pagador", "admin"]:
            count = await collection.count_documents({"role": role})
            print(f"   {role}: {count:,}")
            
    except Exception as e:
        print(f"❌ Error verificando: {e}")
    finally:
        client.close()

async def main():
    """Función principal optimizada"""
    print("⚡ GENERADOR MASIVO OPTIMIZADO - 10M USUARIOS")
    print("="*70)
    
    generator = OptimizedUserGenerator()
    
    try:
        await generator.connect_db()
        
        print(f"\n⚠️ Se generarán {TOTAL_USERS:,} usuarios usando {MAX_WORKERS} workers")
        print("⚡ Proceso optimizado para máxima velocidad")
        response = input("\n🚀 ¿Iniciar generación masiva? (y/N): ")
        
        if response.lower() != 'y':
            print("❌ Cancelado")
            return
        
        await generator.generate_users_parallel()
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Interrumpido. Creados: {generator.users_created:,}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await generator.cleanup()

if __name__ == "__main__":
    # Verificar dependencias
    missing_deps = []
    for dep in ['motor', 'faker', 'bcrypt']:
        try:
            __import__(dep)
        except ImportError:
            missing_deps.append(dep)
    
    if missing_deps:
        print(f"❌ Instalar: pip install {' '.join(missing_deps)}")
        sys.exit(1)
    
    # Ejecutar
    asyncio.run(main())
    
    # Verificación opcional
    verify = input("\n🔍 ¿Verificar resultados? (y/N): ")
    if verify.lower() == 'y':
        asyncio.run(quick_verify())