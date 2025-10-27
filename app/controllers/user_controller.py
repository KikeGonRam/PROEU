from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from pymongo.collection import Collection
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId
import bcrypt
from jose import JWTError, jwt

from app.models.user import (
    UserCreate, UserUpdate, UserResponse, UserInDB, 
    UserLogin, Token, UserListResponse, UserRole, UserStatus
)
from app.config.database import get_database
from app.config.settings import settings

class UserController:
    def __init__(self):
        self.db = get_database()
        self.collection: Collection = self.db.users
        
        # Crear índices
        self.collection.create_index([("email", ASCENDING)], unique=True)
        self.collection.create_index([("created_at", DESCENDING)])

    # Utilidades de contraseña
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña usando bcrypt directamente"""
        try:
            # Asegurar que la contraseña esté en el formato correcto
            password_bytes = plain_password.encode('utf-8')
            hash_bytes = hashed_password.encode('utf-8')
            
            # Verificar con bcrypt
            return bcrypt.checkpw(password_bytes, hash_bytes)
        except Exception as e:
            print(f"Error verificando contraseña: {e}")
            return False

    def get_password_hash(self, password: str) -> str:
        """Crear hash de contraseña usando bcrypt directamente"""
        try:
            # Validar longitud de contraseña
            if len(password) > 72:
                password = password[:72]
            
            # Crear hash
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password_bytes, salt)
            return hashed.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Error al hashear contraseña: {e}")

    # Utilidades JWT
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Crear token de acceso"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[str]:
        """Verificar token JWT y devolver email"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                return None
            return email
        except JWTError:
            return None

    # CRUD Operations
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Crear un nuevo usuario"""
        try:
            # Verificar si el email ya existe
            existing_user = self.collection.find_one({"email": user_data.email})
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El email ya está registrado"
                )

            # Crear hash de la contraseña
            hashed_password = self.get_password_hash(user_data.password)
            
            # Preparar datos del usuario
            user_dict = user_data.dict(exclude={"password"})
            user_dict.update({
                "hashed_password": hashed_password,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": None
            })

            # Insertar en base de datos
            result = self.collection.insert_one(user_dict)
            
            # Obtener el usuario creado
            created_user = self.collection.find_one({"_id": result.inserted_id})
            return UserResponse(**created_user)

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear usuario: {str(e)}"
            )

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Obtener usuario por ID"""
        try:
            if not ObjectId.is_valid(user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ID de usuario inválido"
                )

            user = self.collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                return None
            
            return UserResponse(**user)

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener usuario: {str(e)}"
            )

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Obtener usuario por email (incluye contraseña para autenticación)"""
        try:
            user = self.collection.find_one({"email": email})
            if not user:
                return None
            
            return UserInDB(**user)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener usuario por email: {str(e)}"
            )

    async def get_users(
        self, 
        page: int = 1, 
        limit: int = 10, 
        search: Optional[str] = None,
        role: Optional[UserRole] = None,
        status: Optional[UserStatus] = None
    ) -> UserListResponse:
        """Obtener lista de usuarios con paginación y filtros"""
        try:
            # Construir filtros
            filter_query = {}
            
            if search:
                filter_query["$or"] = [
                    {"first_name": {"$regex": search, "$options": "i"}},
                    {"last_name": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}},
                    {"department": {"$regex": search, "$options": "i"}}
                ]
            
            if role:
                filter_query["role"] = role
                
            if status:
                filter_query["status"] = status

            # Calcular skip
            skip = (page - 1) * limit

            # Obtener total de documentos
            total = self.collection.count_documents(filter_query)

            # Obtener usuarios
            cursor = self.collection.find(filter_query).sort("created_at", DESCENDING).skip(skip).limit(limit)
            users = [UserResponse(**user) for user in cursor]

            # Calcular total de páginas
            total_pages = (total + limit - 1) // limit

            return UserListResponse(
                users=users,
                total=total,
                page=page,
                limit=limit,
                total_pages=total_pages
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener usuarios: {str(e)}"
            )

    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """Actualizar usuario"""
        try:
            if not ObjectId.is_valid(user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ID de usuario inválido"
                )

            # Preparar datos para actualizar
            update_data = {}
            for field, value in user_data.dict(exclude_unset=True).items():
                if field == "password" and value:
                    update_data["hashed_password"] = self.get_password_hash(value)
                elif value is not None:
                    update_data[field] = value

            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No hay datos para actualizar"
                )

            update_data["updated_at"] = datetime.utcnow()

            # Verificar si el email ya existe (si se está actualizando)
            if "email" in update_data:
                existing_user = self.collection.find_one({
                    "email": update_data["email"],
                    "_id": {"$ne": ObjectId(user_id)}
                })
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El email ya está registrado por otro usuario"
                    )

            # Actualizar usuario
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                return None

            # Obtener usuario actualizado
            updated_user = self.collection.find_one({"_id": ObjectId(user_id)})
            return UserResponse(**updated_user)

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar usuario: {str(e)}"
            )

    async def delete_user(self, user_id: str) -> bool:
        """Eliminar usuario"""
        try:
            if not ObjectId.is_valid(user_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ID de usuario inválido"
                )

            result = self.collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar usuario: {str(e)}"
            )

    async def authenticate_user(self, email: str, password: str) -> Optional[UserInDB]:
        """Autenticar usuario"""
        try:
            user = await self.get_user_by_email(email)
            if not user:
                return None
            
            if not self.verify_password(password, user.hashed_password):
                return None
            
            # Actualizar último login
            self.collection.update_one(
                {"_id": user.id},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            return user

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en autenticación: {str(e)}"
            )

    async def login(self, login_data: UserLogin) -> Token:
        """Login de usuario"""
        try:
            user = await self.authenticate_user(login_data.email, login_data.password)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email o contraseña incorrectos",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if user.status != UserStatus.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Usuario inactivo o suspendido"
                )

            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={"sub": user.email}, expires_delta=access_token_expires
            )

            return Token(
                access_token=access_token,
                token_type="bearer",
                user=UserResponse(**user.dict())
            )

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en login: {str(e)}"
            )

    async def refresh_token(self, email: str) -> Token:
        """Renovar token para un usuario existente"""
        try:
            # Buscar usuario
            user = self.collection.find_one({"email": email})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )

            user_obj = UserInDB(**user)

            # Verificar que el usuario esté activo
            if user_obj.status != UserStatus.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Usuario inactivo o suspendido"
                )

            # Crear nuevo token
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={"sub": user_obj.email}, expires_delta=access_token_expires
            )

            return Token(
                access_token=access_token,
                token_type="bearer",
                user=UserResponse(**user_obj.dict())
            )
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error renovando token: {str(e)}"
            )
        

    # Estadísticas para gráficas
    async def get_role_distribution(self):
        """Distribución de usuarios por rol"""
        try:
            pipeline = [
                {"$group": {"_id": "$role", "count": {"$sum": 1}}},
                {"$project": {"role": "$_id", "count": 1, "_id": 0}},
                {"$sort": {"count": -1}}
            ]
            result = list(self.collection.aggregate(pipeline))
            return [{"role": r.get('role') or 'unknown', "count": r.get('count', 0)} for r in result]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_registrations(self, period: str = 'month', start: Optional[datetime] = None, end: Optional[datetime] = None):
        """Altas de usuarios agrupadas por periodo (day, week, month)"""
        try:
            if period == 'day':
                fmt = "%Y-%m-%d"
            elif period == 'week':
                # ISO week as YYYY-ww
                fmt = "%G-%V"
            else:
                fmt = "%Y-%m"

            match = {}
            if start or end:
                match['created_at'] = {}
                if start:
                    match['created_at']['$gte'] = start
                if end:
                    match['created_at']['$lte'] = end

            pipeline = []
            if match:
                pipeline.append({'$match': match})

            pipeline.extend([
                {"$project": {"period": {"$dateToString": {"format": fmt, "date": "$created_at"}}}},
                {"$group": {"_id": "$period", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ])

            result = list(self.collection.aggregate(pipeline))
            # Convertir a etiquetas y datos
            labels = [r['_id'] for r in result]
            data = [r['count'] for r in result]
            return {"labels": labels, "data": data}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_last_login_buckets(self, boundaries = [7,30,90]):
        """Buckets de última conexión: <=7, <=30, <=90, >90"""
        try:
            # boundaries are days
            # Build bucket boundaries in days
            bounds = [0] + boundaries + [100000]
            # We will compute days since last_login and bucket
            # Use an epoch fallback date instead of datetime(0) (which raises)
            epoch = datetime(1970, 1, 1)
            pipeline = [
                {"$project": {"last_login": 1}},
                {"$addFields": {"daysSince": {"$floor": {"$divide": [{"$subtract": ["$$NOW", {"$ifNull": ["$last_login", epoch]}]}, 1000*60*60*24]}}}},
                {"$bucket": {"groupBy": "$daysSince", "boundaries": [0,7,30,90,100000], "default": ">=", "output": {"count": {"$sum": 1}}}}
            ]
            agg = list(self.collection.aggregate(pipeline))
            # Map results to known labels
            mapping = {0: 0, 7: 0, 30: 0, 90: 0, '>=': 0}
            for item in agg:
                b = item.get('_id')
                c = item.get('count', 0)
                mapping[b] = mapping.get(b, 0) + c

            labels = ['Últimos 7 días', 'Últimos 30 días', 'Últimos 90 días', '> 90 días']
            # The bucket aggregation above uses boundaries 0,7,30,90,100000 with _id equal to the lower boundary of the bucket.
            bucket_map = {0:0,7:0,30:0,90:0,'>=':0}
            for it in agg:
                key = it.get('_id')
                cnt = it.get('count',0)
                if key == 0:
                    bucket_map[0] += cnt
                elif key == 7:
                    bucket_map[7] += cnt
                elif key == 30:
                    bucket_map[30] += cnt
                elif key == 90:
                    bucket_map[90] += cnt
                else:
                    bucket_map['>='] += cnt

            data = [bucket_map[7], bucket_map[30], bucket_map[90], bucket_map['>=']]
            return {"labels": labels, "data": data}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def get_departments_top(self, top: int = 10):
        """Top N departamentos por número de usuarios"""
        try:
            pipeline = [
                {"$group": {"_id": "$department", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": top},
                {"$project": {"department": "$_id", "count": 1, "_id": 0}}
            ]
            res = list(self.collection.aggregate(pipeline))
            labels = [r.get('department') or 'Sin departamento' for r in res]
            data = [r.get('count',0) for r in res]
            return {"labels": labels, "data": data}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Instancia global del controlador
user_controller = UserController()