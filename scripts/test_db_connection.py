from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test_connection():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["sistema_solicitudes_pagos"]
    collection = db["solicitudes_estandar"]

    try:
        count = await collection.count_documents({})
        print(f"Total documentos en la colección 'solicitudes_estandar': {count}")
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())