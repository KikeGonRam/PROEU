#!/usr/bin/env python3
"""
Script de utilidades para gestionar usuarios masivos
Incluye funciones para limpiar, verificar y mantener la base de datos

Autor: Sistema EU-UTVT
Fecha: Octubre 2025
"""

import asyncio
import time
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import sys

# Configuración
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "eu_utvt_db"
COLLECTION_NAME = "users"

class UserDatabaseManager:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
    
    async def connect(self):
        """Conectar a MongoDB"""
        try:
            self.client = AsyncIOMotorClient(MONGO_URI)
            self.db = self.client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]
            await self.client.admin.command('ping')
            print("✅ Conectado a MongoDB")
        except Exception as e:
            print(f"❌ Error conectando: {e}")
            sys.exit(1)
    
    async def get_database_stats(self):
        """Obtener estadísticas completas de la base de datos"""
        print("📊 ESTADÍSTICAS DE BASE DE DATOS")
        print("="*50)
        
        # Estadísticas básicas
        total_users = await self.collection.count_documents({})
        active_users = await self.collection.count_documents({"is_active": True})
        generated_users = await self.collection.count_documents({"metadata.source": "massive_generation"})
        
        print(f"👥 Total usuarios: {total_users:,}")
        print(f"✅ Usuarios activos: {active_users:,}")
        print(f"🤖 Usuarios generados: {generated_users:,}")
        print(f"👤 Usuarios reales: {total_users - generated_users:,}")
        
        # Distribución por roles
        print(f"\n📋 Distribución por roles:")
        roles_pipeline = [
            {"$group": {"_id": "$role", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        async for role_data in self.collection.aggregate(roles_pipeline):
            role = role_data["_id"]
            count = role_data["count"]
            percentage = (count / total_users) * 100 if total_users > 0 else 0
            print(f"   {role.capitalize()}: {count:,} ({percentage:.1f}%)")
        
        # Distribución por departamentos
        print(f"\n🏢 Top 10 departamentos:")
        dept_pipeline = [
            {"$group": {"_id": "$department", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        async for dept_data in self.collection.aggregate(dept_pipeline):
            dept = dept_data["_id"]
            count = dept_data["count"]
            print(f"   {dept}: {count:,}")
        
        # Estadísticas de actividad
        users_with_login = await self.collection.count_documents({"last_login": {"$ne": None}})
        print(f"\n📱 Usuarios con login: {users_with_login:,}")
        
        # Tamaño de colección
        stats = await self.db.command("collStats", COLLECTION_NAME)
        size_mb = stats.get("size", 0) / (1024 * 1024)
        print(f"💾 Tamaño colección: {size_mb:.2f} MB")
        
        # Índices
        indexes = await self.collection.list_indexes().to_list(length=None)
        print(f"📚 Índices creados: {len(indexes)}")
        
        print("="*50)
    
    async def cleanup_generated_users(self):
        """Limpiar usuarios generados automáticamente"""
        print("🧹 LIMPIEZA DE USUARIOS GENERADOS")
        print("="*40)
        
        # Contar usuarios a eliminar
        to_delete = await self.collection.count_documents({"metadata.source": "massive_generation"})
        
        if to_delete == 0:
            print("✅ No hay usuarios generados para limpiar")
            return
        
        print(f"⚠️ Se eliminarán {to_delete:,} usuarios generados")
        confirm = input("¿Continuar? (escriba 'CONFIRMAR'): ")
        
        if confirm != "CONFIRMAR":
            print("❌ Operación cancelada")
            return
        
        # Eliminar en lotes para mejor rendimiento
        batch_size = 10000
        deleted_total = 0
        
        while True:
            result = await self.collection.delete_many(
                {"metadata.source": "massive_generation"},
                {"limit": batch_size}
            )
            
            deleted_count = result.deleted_count
            deleted_total += deleted_count
            
            if deleted_count == 0:
                break
            
            print(f"🗑️ Eliminados: {deleted_total:,}/{to_delete:,}")
        
        print(f"✅ Limpieza completada. {deleted_total:,} usuarios eliminados")
    
    async def optimize_database(self):
        """Optimizar la base de datos después de operaciones masivas"""
        print("⚡ OPTIMIZACIÓN DE BASE DE DATOS")
        print("="*40)
        
        try:
            # Compactar colección
            print("🔧 Compactando colección...")
            await self.db.command("compact", COLLECTION_NAME)
            print("✅ Colección compactada")
            
            # Reindexar
            print("📚 Reindexando...")
            await self.collection.reindex()
            print("✅ Reindexado completado")
            
            # Actualizar estadísticas
            print("📊 Actualizando estadísticas...")
            await self.db.command("planCacheClear", COLLECTION_NAME)
            print("✅ Estadísticas actualizadas")
            
        except Exception as e:
            print(f"⚠️ Error en optimización: {e}")
    
    async def create_sample_export(self, sample_size=1000):
        """Crear export de muestra de usuarios"""
        print(f"📤 EXPORTANDO MUESTRA DE {sample_size:,} USUARIOS")
        print("="*50)
        
        try:
            # Obtener muestra representativa
            pipeline = [
                {"$sample": {"size": sample_size}},
                {"$project": {
                    "user_id": 1,
                    "email": 1,
                    "first_name": 1,
                    "last_name": 1,
                    "role": 1,
                    "department": 1,
                    "is_active": 1,
                    "created_at": 1
                }}
            ]
            
            sample_users = await self.collection.aggregate(pipeline).to_list(length=sample_size)
            
            # Exportar a archivo
            import json
            filename = f"sample_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(sample_users, f, indent=2, default=str, ensure_ascii=False)
            
            print(f"✅ Muestra exportada a: {filename}")
            print(f"📊 Usuarios exportados: {len(sample_users):,}")
            
        except Exception as e:
            print(f"❌ Error exportando: {e}")
    
    async def verify_data_integrity(self):
        """Verificar integridad de datos"""
        print("🔍 VERIFICACIÓN DE INTEGRIDAD")
        print("="*40)
        
        issues = []
        
        # Verificar emails únicos
        print("📧 Verificando emails únicos...")
        duplicate_emails = await self.collection.aggregate([
            {"$group": {"_id": "$email", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}}
        ]).to_list(length=None)
        
        if duplicate_emails:
            issues.append(f"Emails duplicados: {len(duplicate_emails)}")
        
        # Verificar user_ids únicos
        print("🆔 Verificando user_ids únicos...")
        duplicate_ids = await self.collection.aggregate([
            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}}
        ]).to_list(length=None)
        
        if duplicate_ids:
            issues.append(f"User IDs duplicados: {len(duplicate_ids)}")
        
        # Verificar campos requeridos
        print("📝 Verificando campos requeridos...")
        required_fields = ["email", "password", "first_name", "last_name", "role"]
        
        for field in required_fields:
            missing = await self.collection.count_documents({field: {"$exists": False}})
            if missing > 0:
                issues.append(f"Campo {field} faltante en {missing} usuarios")
        
        # Verificar roles válidos
        print("👤 Verificando roles válidos...")
        valid_roles = ["solicitante", "aprobador", "pagador", "admin"]
        invalid_roles = await self.collection.count_documents({"role": {"$nin": valid_roles}})
        
        if invalid_roles > 0:
            issues.append(f"Roles inválidos: {invalid_roles}")
        
        # Resultados
        if not issues:
            print("✅ Integridad de datos verificada - Sin problemas")
        else:
            print("⚠️ Problemas encontrados:")
            for issue in issues:
                print(f"   - {issue}")
    
    async def performance_test(self):
        """Realizar pruebas de rendimiento básicas"""
        print("🚀 PRUEBAS DE RENDIMIENTO")
        print("="*40)
        
        # Test 1: Búsqueda por email
        print("📧 Test: Búsqueda por email...")
        start_time = time.time()
        result = await self.collection.find_one({"email": "user1000@utvt.edu.mx"})
        email_time = time.time() - start_time
        print(f"   Tiempo: {email_time*1000:.2f}ms")
        
        # Test 2: Conteo por role
        print("👤 Test: Conteo por role...")
        start_time = time.time()
        count = await self.collection.count_documents({"role": "solicitante"})
        role_time = time.time() - start_time
        print(f"   Tiempo: {role_time*1000:.2f}ms | Resultado: {count:,}")
        
        # Test 3: Agregación compleja
        print("📊 Test: Agregación compleja...")
        start_time = time.time()
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {"_id": {"role": "$role", "dept": "$department"}, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        results = await self.collection.aggregate(pipeline).to_list(length=10)
        agg_time = time.time() - start_time
        print(f"   Tiempo: {agg_time*1000:.2f}ms | Resultados: {len(results)}")
        
        # Test 4: Inserción individual
        print("➕ Test: Inserción individual...")
        test_user = {
            "user_id": 99999999,
            "email": "test_performance@test.com",
            "password": "test_hash",
            "first_name": "Test",
            "last_name": "Performance",
            "role": "solicitante",
            "department": "Test",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "metadata": {"source": "performance_test"}
        }
        
        start_time = time.time()
        await self.collection.insert_one(test_user)
        insert_time = time.time() - start_time
        print(f"   Tiempo: {insert_time*1000:.2f}ms")
        
        # Limpiar test
        await self.collection.delete_one({"user_id": 99999999})
        
        print(f"\n📈 Resumen de rendimiento:")
        print(f"   Búsqueda por email: {email_time*1000:.2f}ms")
        print(f"   Conteo por role: {role_time*1000:.2f}ms")
        print(f"   Agregación compleja: {agg_time*1000:.2f}ms")
        print(f"   Inserción: {insert_time*1000:.2f}ms")
    
    async def cleanup(self):
        """Cerrar conexiones"""
        if self.client:
            self.client.close()

async def main():
    """Menú principal"""
    manager = UserDatabaseManager()
    await manager.connect()
    
    while True:
        print("\n" + "="*50)
        print("🛠️ GESTOR DE USUARIOS MASIVOS - EU-UTVT")
        print("="*50)
        print("1. 📊 Ver estadísticas de base de datos")
        print("2. 🧹 Limpiar usuarios generados")
        print("3. ⚡ Optimizar base de datos")
        print("4. 📤 Exportar muestra de usuarios")
        print("5. 🔍 Verificar integridad de datos")
        print("6. 🚀 Pruebas de rendimiento")
        print("7. ❌ Salir")
        print("-"*50)
        
        try:
            option = input("Selecciona una opción (1-7): ").strip()
            
            if option == "1":
                await manager.get_database_stats()
            elif option == "2":
                await manager.cleanup_generated_users()
            elif option == "3":
                await manager.optimize_database()
            elif option == "4":
                size = input("Tamaño de muestra (default 1000): ").strip()
                size = int(size) if size.isdigit() else 1000
                await manager.create_sample_export(size)
            elif option == "5":
                await manager.verify_data_integrity()
            elif option == "6":
                await manager.performance_test()
            elif option == "7":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")
                
        except KeyboardInterrupt:
            print("\n👋 Saliendo...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    await manager.cleanup()

if __name__ == "__main__":
    asyncio.run(main())