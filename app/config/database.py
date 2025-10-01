from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.config.settings import settings
import logging

# Cliente MongoDB para operaciones síncronas
mongo_client: MongoClient = None
database = None

# Cliente MongoDB para operaciones asíncronas 
async_mongo_client: AsyncIOMotorClient = None
async_database = None

def init_sync_database():
    """Inicializar la base de datos síncrona"""
    global mongo_client, database
    
    try:
        mongo_client = MongoClient(settings.MONGODB_URL)
        database = mongo_client[settings.DATABASE_NAME]
        # Verificar conexión
        mongo_client.admin.command('ping')
        logging.info("Conectado exitosamente a MongoDB (síncrono)")
        return database
    except Exception as e:
        logging.error(f"Error al conectar a MongoDB: {e}")
        raise

async def connect_to_mongo():
    """Conectar a MongoDB"""
    global mongo_client, database, async_mongo_client, async_database
    
    try:
        # Cliente síncrono (si no existe)
        if not mongo_client:
            mongo_client = MongoClient(settings.MONGODB_URL)
            database = mongo_client[settings.DATABASE_NAME]
        
        # Cliente asíncrono
        async_mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
        async_database = async_mongo_client[settings.DATABASE_NAME]
        
        # Verificar conexión
        await async_mongo_client.admin.command('ping')
        logging.info("Conectado exitosamente a MongoDB")
        
    except Exception as e:
        logging.error(f"Error al conectar a MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Cerrar conexión a MongoDB"""
    global mongo_client, async_mongo_client
    
    if mongo_client:
        mongo_client.close()
    if async_mongo_client:
        async_mongo_client.close()
    logging.info("Conexión a MongoDB cerrada")

def get_database():
    """Obtener instancia de la base de datos síncrona"""
    if database is None:
        init_sync_database()
    return database

def get_async_database():
    """Obtener instancia de la base de datos asíncrona"""
    return async_database