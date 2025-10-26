from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

class UserDB:
    def __init__(self, db):
        self.collection = db["users"]

    async def count_documents(self):
        """Cuenta el número total de usuarios activos en la colección."""
        return await self.collection.count_documents({"status": "active"})

    async def find_user_by_email(self, email):
        """Busca un usuario por su correo electrónico."""
        return await self.collection.find_one({"email": email})

    async def create_user(self, user_data):
        """Crea un nuevo usuario en la base de datos."""
        result = await self.collection.insert_one(user_data)
        return str(result.inserted_id)

    async def update_user(self, user_id, update_data):
        """Actualiza un usuario existente."""
        result = await self.collection.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})
        return result.modified_count

    async def delete_user(self, user_id):
        """Elimina un usuario por su ID."""
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count