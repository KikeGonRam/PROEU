from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from typing import List, Optional
from datetime import datetime
import os
from app.models.solicitud import SolicitudEstandarCreate, SolicitudEstandar, SolicitudEstandarUpdate, EstadoSolicitud
from app.config.database import get_database
from app.routes.user_routes import get_current_user
from app.models.user import UserResponse
from bson import ObjectId
import json

router = APIRouter(tags=["Solicitudes"])

# Directorio para archivos subidos
UPLOAD_DIR = "uploads/solicitudes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/test", summary="Probar conexión a base de datos")
async def test_database(db = Depends(get_database)):
    """
    Endpoint de prueba para verificar la conexión a la base de datos
    """
    try:
        # Verificar conexión
        collections = db.list_collection_names()
        return {
            "message": "Conexión exitosa",
            "collections": collections,
            "database_name": db.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión: {str(e)}")

@router.post("/estandar", summary="Crear nueva solicitud estándar")
async def crear_solicitud_estandar(
    solicitud: SolicitudEstandarCreate,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Crear una nueva solicitud estándar
    """
    try:
        print(f"Usuario actual: {current_user.email}, rol: {current_user.role}")
        print(f"Datos recibidos: {solicitud}")
        
        # Verificar que el usuario sea solicitante o administrador
        if current_user.role not in ["solicitante", "admin"]:
            raise HTTPException(status_code=403, detail="Solo los solicitantes o administradores pueden crear solicitudes")
        
        # Crear objeto solicitud
        solicitud_data = {
            "departamento": solicitud.departamento,
            "monto": solicitud.monto,
            "tipo_moneda": solicitud.tipo_moneda,
            "banco_destino": solicitud.banco_destino,
            "cuenta_destino": solicitud.cuenta_destino,
            "es_clabe": solicitud.es_clabe,
            "nombre_beneficiario": solicitud.nombre_beneficiario,
            "nombre_empresa": solicitud.nombre_empresa,
            "segundo_beneficiario": solicitud.segundo_beneficiario,
            "tipo_pago": solicitud.tipo_pago,
            "concepto_pago": solicitud.concepto_pago,
            "concepto_otros": solicitud.concepto_otros,
            "fecha_limite_pago": solicitud.fecha_limite_pago,
            "descripcion_tipo_pago": solicitud.descripcion_tipo_pago,
            "comentarios_solicitante": solicitud.comentarios_solicitante,
            "archivos_adjuntos": [],
            "solicitante_email": current_user.email,
            "estado": EstadoSolicitud.ENVIADA,
            "fecha_creacion": datetime.utcnow(),
            "fecha_actualizacion": datetime.utcnow()
        }
        
        # Insertar en la base de datos
        collection = db["solicitudes_estandar"]
        result = collection.insert_one(solicitud_data)
        
        # Obtener la solicitud creada
        solicitud_creada = collection.find_one({"_id": result.inserted_id})
        solicitud_creada["id"] = str(solicitud_creada["_id"])
        del solicitud_creada["_id"]
        
        return {
            "message": "Solicitud creada exitosamente",
            "solicitud_id": solicitud_creada["id"],
            "solicitud": solicitud_creada
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear la solicitud: {str(e)}")

@router.post("/estandar/borrador", summary="Guardar solicitud estándar como borrador")
async def guardar_borrador_estandar(
    solicitud: SolicitudEstandarCreate,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Guardar una solicitud estándar como borrador
    """
    try:
        # Verificar que el usuario sea solicitante o administrador
        if current_user.role not in ["solicitante", "admin"]:
            raise HTTPException(status_code=403, detail="Solo los solicitantes o administradores pueden crear solicitudes")
        
        # Crear objeto solicitud como borrador
        solicitud_data = {
            "departamento": solicitud.departamento,
            "monto": solicitud.monto,
            "tipo_moneda": solicitud.tipo_moneda,
            "banco_destino": solicitud.banco_destino,
            "cuenta_destino": solicitud.cuenta_destino,
            "es_clabe": solicitud.es_clabe,
            "nombre_beneficiario": solicitud.nombre_beneficiario,
            "nombre_empresa": solicitud.nombre_empresa,
            "segundo_beneficiario": solicitud.segundo_beneficiario,
            "tipo_pago": solicitud.tipo_pago,
            "concepto_pago": solicitud.concepto_pago,
            "concepto_otros": solicitud.concepto_otros,
            "fecha_limite_pago": solicitud.fecha_limite_pago,
            "descripcion_tipo_pago": solicitud.descripcion_tipo_pago,
            "comentarios_solicitante": solicitud.comentarios_solicitante,
            "archivos_adjuntos": [],
            "solicitante_email": current_user.email,
            "estado": EstadoSolicitud.BORRADOR,
            "fecha_creacion": datetime.utcnow(),
            "fecha_actualizacion": datetime.utcnow()
        }
        
        # Insertar en la base de datos
        collection = db["solicitudes_estandar"]
        result = collection.insert_one(solicitud_data)
        
        return {
            "message": "Borrador guardado exitosamente",
            "solicitud_id": str(result.inserted_id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar el borrador: {str(e)}")

@router.get("/mis-solicitudes", summary="Obtener solicitudes del usuario actual")
async def obtener_mis_solicitudes(
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Obtener todas las solicitudes del usuario actual
    """
    try:
        collection = db["solicitudes_estandar"]

        # Si el usuario es admin, retornar todas las solicitudes; si no, solo las del solicitante
        if current_user.role == "admin":
            solicitudes = list(collection.find({}))
        else:
            # Buscar solicitudes del usuario
            solicitudes = list(collection.find({"solicitante_email": current_user.email}))
        
        # Convertir ObjectId a string
        for solicitud in solicitudes:
            solicitud["id"] = str(solicitud["_id"])
            del solicitud["_id"]
        
        return {"solicitudes": solicitudes}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener solicitudes: {str(e)}")

@router.get("/estadisticas", summary="Obtener estadísticas de solicitudes del usuario")
async def obtener_estadisticas(
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Obtener estadísticas de solicitudes del usuario actual
    """
    try:
        collection = db["solicitudes_estandar"]

        # Contar solicitudes por estado
        if current_user.role == "admin":
            # Admins ven estadísticas globales
            pipeline = [
                {"$group": {
                    "_id": "$estado",
                    "count": {"$sum": 1},
                    "total_monto": {"$sum": "$monto"}
                }}
            ]
        else:
            pipeline = [
                {"$match": {"solicitante_email": current_user.email}},
                {"$group": {
                    "_id": "$estado",
                    "count": {"$sum": 1},
                    "total_monto": {"$sum": "$monto"}
                }}
            ]
        
        resultados = list(collection.aggregate(pipeline))
        
        # Organizar estadísticas
        estadisticas = {
            "total": 0,
            "pendientes": 0,
            "aprobadas": 0,
            "rechazadas": 0,
            "borradores": 0,
            "monto_total": 0
        }
        
        for resultado in resultados:
            estado = resultado["_id"]
            count = resultado["count"]
            monto = resultado.get("total_monto", 0)
            
            estadisticas["total"] += count
            estadisticas["monto_total"] += monto
            
            if estado in ["enviada", "en_revision"]:
                estadisticas["pendientes"] += count
            elif estado == "aprobada":
                estadisticas["aprobadas"] += count
            elif estado == "rechazada":
                estadisticas["rechazadas"] += count
            elif estado == "borrador":
                estadisticas["borradores"] += count
        
        return estadisticas
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

@router.post("/upload-files/{solicitud_id}", summary="Subir archivos a una solicitud")
async def subir_archivos(
    solicitud_id: str,
    files: List[UploadFile] = File(...),
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Subir archivos adjuntos a una solicitud
    """
    try:
        collection = db["solicitudes_estandar"]
        
        # Verificar que la solicitud existe
        solicitud = collection.find_one({
            "_id": ObjectId(solicitud_id)
        })
        
        if not solicitud:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")

        # Permitir al solicitante propietario o al admin subir archivos
        if solicitud.get("solicitante_email") != current_user.email and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="No tienes permisos para subir archivos a esta solicitud")
        
        # Procesar archivos
        archivos_guardados = []
        for file in files:
            # Generar nombre único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            filepath = os.path.join(UPLOAD_DIR, filename)
            
            # Guardar archivo
            with open(filepath, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Información del archivo
            archivo_info = {
                "nombre_archivo": file.filename,
                "tipo_archivo": file.content_type,
                "tamaño": len(content),
                "ruta_archivo": filename,  # Solo el nombre del archivo, no la ruta completa
                "fecha_subida": datetime.utcnow()
            }
            
            archivos_guardados.append(archivo_info)
        
        # Actualizar solicitud con archivos
        collection.update_one(
            {"_id": ObjectId(solicitud_id)},
            {
                "$push": {"archivos_adjuntos": {"$each": archivos_guardados}},
                "$set": {"fecha_actualizacion": datetime.utcnow()}
            }
        )
        
        return {
            "message": f"{len(archivos_guardados)} archivos subidos exitosamente",
            "archivos": archivos_guardados
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir archivos: {str(e)}")

@router.get("/estandar/{solicitud_id}", summary="Obtener solicitud estándar por ID")
async def obtener_solicitud_por_id(
    solicitud_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Obtener una solicitud estándar específica por ID
    """
    try:
        collection = db["solicitudes_estandar"]
        
        # Buscar la solicitud
        solicitud = collection.find_one({"_id": ObjectId(solicitud_id)})
        
        if not solicitud:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        
        # Verificar permisos: el usuario debe ser el creador, aprobador, pagador o admin
        if (current_user.role not in ["admin", "aprobador", "pagador"] and 
            solicitud.get("solicitante_email") != current_user.email):
            raise HTTPException(status_code=403, detail="No tienes permisos para ver esta solicitud")
        
        # Convertir ObjectId a string
        solicitud["id"] = str(solicitud["_id"])
        del solicitud["_id"]
        
        return {"solicitud": solicitud}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error al obtener solicitud: {str(e)}")

@router.put("/estandar/{solicitud_id}", summary="Actualizar solicitud estándar")
async def actualizar_solicitud_estandar(
    solicitud_id: str,
    solicitud_update: SolicitudEstandarUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Actualizar una solicitud estándar existente
    Solo el creador puede actualizar si está en estado borrador o pendiente
    """
    try:
        collection = db["solicitudes_estandar"]
        
        # Buscar la solicitud
        solicitud_existente = collection.find_one({"_id": ObjectId(solicitud_id)})
        
        if not solicitud_existente:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        
        # Verificar permisos: el propietario o el admin pueden editar
        if solicitud_existente.get("solicitante_email") != current_user.email and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Solo el propietario o un administrador pueden editar esta solicitud")
        
        # Verificar estado: solo se pueden editar borradores y pendientes
        estado_actual = solicitud_existente.get("estado", "borrador")
        if estado_actual not in ["borrador", "pendiente"]:
            raise HTTPException(status_code=400, detail="Solo se pueden editar solicitudes en estado borrador o pendiente")
        
        # Preparar datos de actualización (solo campos no None)
        update_data = {}
        for field, value in solicitud_update.dict(exclude_unset=True).items():
            if value is not None:
                update_data[field] = value
        
        # Agregar fecha de actualización
        update_data["fecha_actualizacion"] = datetime.utcnow()
        
        # Realizar actualización
        result = collection.update_one(
            {"_id": ObjectId(solicitud_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No se realizaron cambios")
        
        # Obtener solicitud actualizada
        solicitud_actualizada = collection.find_one({"_id": ObjectId(solicitud_id)})
        solicitud_actualizada["id"] = str(solicitud_actualizada["_id"])
        del solicitud_actualizada["_id"]
        
        return {
            "message": "Solicitud actualizada exitosamente",
            "solicitud": solicitud_actualizada
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error al actualizar solicitud: {str(e)}")

@router.delete("/estandar/{solicitud_id}", summary="Eliminar solicitud estándar")
async def eliminar_solicitud_estandar(
    solicitud_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Eliminar una solicitud estándar
    Solo el creador puede eliminar si está en estado borrador
    """
    try:
        collection = db["solicitudes_estandar"]
        
        # Buscar la solicitud
        solicitud = collection.find_one({"_id": ObjectId(solicitud_id)})
        
        if not solicitud:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        
        # Verificar permisos: el propietario o el admin pueden eliminar
        if solicitud.get("solicitante_email") != current_user.email and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Solo el propietario o un administrador pueden eliminar esta solicitud")
        
        # Verificar estado: solo se pueden eliminar borradores
        estado_actual = solicitud.get("estado", "borrador")
        if estado_actual != "borrador":
            raise HTTPException(status_code=400, detail="Solo se pueden eliminar solicitudes en estado borrador")
        
        # Eliminar archivos asociados si existen
        archivos = solicitud.get("archivos_adjuntos", [])
        for archivo in archivos:
            ruta_archivo = archivo.get("ruta_archivo")
            if ruta_archivo:
                archivo_path = os.path.join(UPLOAD_DIR, ruta_archivo)
                if os.path.exists(archivo_path):
                    try:
                        os.remove(archivo_path)
                    except Exception as e:
                        print(f"Error eliminando archivo {archivo_path}: {e}")
        
        # Eliminar solicitud de la base de datos
        result = collection.delete_one({"_id": ObjectId(solicitud_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=400, detail="No se pudo eliminar la solicitud")
        
        return {"message": "Solicitud eliminada exitosamente"}
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error al eliminar solicitud: {str(e)}")

@router.get("/todas", summary="Obtener todas las solicitudes (Admin/Aprobador/Pagador)")
async def obtener_todas_solicitudes(
    estado: Optional[str] = None,
    departamento: Optional[str] = None,
    limit: int = 50,
    skip: int = 0,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Obtener todas las solicitudes con filtros opcionales
    Solo para usuarios con rol admin, aprobador o pagador
    """
    try:
        # Verificar permisos
        if current_user.role not in ["admin", "aprobador", "pagador"]:
            raise HTTPException(status_code=403, detail="No tienes permisos para ver todas las solicitudes")
        
        collection = db["solicitudes_estandar"]
        
        # Construir filtros
        filtros = {}
        if estado:
            filtros["estado"] = estado
        if departamento:
            filtros["departamento"] = departamento
        
        # Obtener solicitudes con paginación
        cursor = collection.find(filtros).sort("fecha_creacion", -1).skip(skip).limit(limit)
        solicitudes = list(cursor)
        
        # Convertir ObjectId a string
        for solicitud in solicitudes:
            solicitud["id"] = str(solicitud["_id"])
            del solicitud["_id"]
        
        # Obtener total para paginación
        total = collection.count_documents(filtros)
        
        return {
            "solicitudes": solicitudes,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error al obtener solicitudes: {str(e)}")

@router.patch("/estandar/{solicitud_id}/estado", summary="Cambiar estado de solicitud")
async def cambiar_estado_solicitud(
    solicitud_id: str,
    nuevo_estado: EstadoSolicitud,
    comentarios: Optional[str] = None,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_database)
):
    """
    Cambiar el estado de una solicitud estándar
    Solo usuarios con permisos específicos pueden cambiar estados
    """
    try:
        collection = db["solicitudes_estandar"]
        
        # Buscar la solicitud
        solicitud = collection.find_one({"_id": ObjectId(solicitud_id)})
        
        if not solicitud:
            raise HTTPException(status_code=404, detail="Solicitud no encontrada")
        
        estado_actual = solicitud.get("estado", "borrador")
        
        # Verificar permisos según el cambio de estado
        if nuevo_estado == "pendiente" and current_user.role != "solicitante":
            raise HTTPException(status_code=403, detail="Solo el solicitante puede enviar la solicitud")
        elif nuevo_estado in ["aprobada", "rechazada"] and current_user.role not in ["admin", "aprobador"]:
            raise HTTPException(status_code=403, detail="Solo administradores y aprobadores pueden aprobar/rechazar")
        elif nuevo_estado == "pagada" and current_user.role not in ["admin", "pagador"]:
            raise HTTPException(status_code=403, detail="Solo administradores y pagadores pueden marcar como pagada")
        
        # Validar transiciones de estado válidas
        transiciones_validas = {
            "borrador": ["pendiente"],
            "pendiente": ["aprobada", "rechazada"],
            "aprobada": ["pagada"],
            "rechazada": ["pendiente"],  # Permitir reenvío
            "pagada": []  # Estado final
        }
        
        if nuevo_estado not in transiciones_validas.get(estado_actual, []):
            raise HTTPException(
                status_code=400, 
                detail=f"No se puede cambiar de estado '{estado_actual}' a '{nuevo_estado}'"
            )
        
        # Preparar actualización
        update_data = {
            "estado": nuevo_estado,
            "fecha_actualizacion": datetime.utcnow()
        }
        
        # Agregar información del aprobador/pagador
        if nuevo_estado in ["aprobada", "rechazada"]:
            update_data["aprobador_email"] = current_user.email
            update_data["fecha_aprobacion"] = datetime.utcnow()
        elif nuevo_estado == "pagada":
            update_data["pagador_email"] = current_user.email
            update_data["fecha_pago"] = datetime.utcnow()
        
        # Agregar comentarios si se proporcionan
        if comentarios:
            update_data["comentarios_" + current_user.role] = comentarios
        
        # Realizar actualización
        result = collection.update_one(
            {"_id": ObjectId(solicitud_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No se pudo actualizar el estado")
        
        return {
            "message": f"Estado cambiado a '{nuevo_estado}' exitosamente",
            "nuevo_estado": nuevo_estado
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error al cambiar estado: {str(e)}")