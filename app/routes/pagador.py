"""
Rutas para el dashboard del Pagador
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
import json
from datetime import datetime
from bson import ObjectId

from app.middleware.auth_middleware import require_role
from app.controllers.pagador_controller import pagador_controller
from app.models.solicitud import SolicitudPago, SolicitudComprobantesPago
import os
import shutil


# Configurar router y templates
router = APIRouter(prefix="/pagador", tags=["pagador"])
templates = Jinja2Templates(directory="templates")

# Configurar directorio para archivos
UPLOAD_DIR = os.path.join("static", "uploads", "comprobantes")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Encoder personalizado para JSON
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


@router.get("/dashboard")
async def dashboard_pagador(
    current_user: dict = Depends(require_role("pagador"))
):
    """
    Página principal del dashboard del pagador
    
    Requiere rol: pagador
    """
    try:
        return templates.TemplateResponse(
            "dashboards/pagador.html",
            {
                "request": {},
                "user": current_user
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cargar dashboard: {str(e)}"
        )


@router.get("/api/solicitudes-aprobadas")
async def get_solicitudes_aprobadas(
    filtro_departamento: Optional[str] = None,
    filtro_tipo_pago: Optional[str] = None,
    current_user: dict = Depends(require_role("pagador"))
):
    """
    Obtener todas las solicitudes aprobadas (pendientes de pago)
    
    Requiere rol: pagador
    
    Query params:
    - filtro_departamento: Filtrar por departamento
    - filtro_tipo_pago: Filtrar por tipo de pago
    """
    try:
        print(f"\n🔍 GET /api/solicitudes-aprobadas - Usuario: {current_user['email']}")
        print(f"📌 Filtros: departamento={filtro_departamento}, tipo_pago={filtro_tipo_pago}")
        
        resultado = pagador_controller.get_solicitudes_aprobadas(
            pagador_email=current_user["email"],
            filtro_departamento=filtro_departamento,
            filtro_tipo_pago=filtro_tipo_pago
        )
        
        print(f"✅ Solicitudes encontradas: {resultado['total']}")
        
        # Serializar con el encoder personalizado
        json_content = json.dumps(resultado, cls=DateTimeEncoder, ensure_ascii=False)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=json.loads(json_content)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR en get_solicitudes_aprobadas endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener solicitudes: {str(e)}"
        )


@router.get("/api/estadisticas")
async def get_estadisticas(
    current_user: dict = Depends(require_role("pagador"))
):
    """
    Obtener estadísticas del dashboard
    
    Requiere rol: pagador
    """
    try:
        estadisticas = pagador_controller.get_estadisticas_pagador(
            pagador_email=current_user["email"]
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "estadisticas": estadisticas
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/api/historial")
async def get_historial_pagador(
    filtro_estado: Optional[str] = None,
    filtro_departamento: Optional[str] = None,
    filtro_tipo_pago: Optional[str] = None,
    current_user: dict = Depends(require_role("pagador"))
):
    """
    Obtener historial de solicitudes pagadas por el pagador
    
    Query params:
        - filtro_estado: Filtrar por estado (opcional)
        - filtro_departamento: Filtrar por departamento (opcional)
        - filtro_tipo_pago: Filtrar por tipo de pago (opcional)
    
    Requiere rol: pagador
    """
    try:
        resultado = pagador_controller.get_historial_pagador(
            pagador_email=current_user["email"],
            filtro_estado=filtro_estado,
            filtro_departamento=filtro_departamento,
            filtro_tipo_pago=filtro_tipo_pago
        )
        
        # Convertir a JSON con el encoder personalizado
        json_content = json.loads(
            json.dumps(resultado, cls=DateTimeEncoder)
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=json_content
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/api/pendientes-comprobante")
async def get_pendientes_comprobante(
    filtro_departamento: Optional[str] = None,
    filtro_tipo_pago: Optional[str] = None,
    current_user: dict = Depends(require_role("pagador"))
):
    """
    Obtener solicitudes pagadas que necesitan comprobantes
    
    Query params:
        - filtro_departamento: Filtrar por departamento (opcional)
        - filtro_tipo_pago: Filtrar por tipo de pago (opcional)
    
    Requiere rol: pagador
    """
    try:
        resultado = pagador_controller.get_solicitudes_pendientes_comprobante(
            pagador_email=current_user["email"],
            filtro_departamento=filtro_departamento,
            filtro_tipo_pago=filtro_tipo_pago
        )
        
        # Convertir a JSON con el encoder personalizado
        json_content = json.loads(
            json.dumps(resultado, cls=DateTimeEncoder)
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=json_content
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.get("/api/con-comprobantes")
async def get_con_comprobantes(
    filtro_departamento: Optional[str] = None,
    filtro_tipo_pago: Optional[str] = None,
    current_user: dict = Depends(require_role("pagador"))
):
    """
    Obtener solicitudes que ya tienen comprobantes subidos
    
    Query params:
        - filtro_departamento: Filtrar por departamento (opcional)
        - filtro_tipo_pago: Filtrar por tipo de pago (opcional)
    
    Requiere rol: pagador
    """
    try:
        resultado = pagador_controller.get_solicitudes_con_comprobantes(
            pagador_email=current_user["email"],
            filtro_departamento=filtro_departamento,
            filtro_tipo_pago=filtro_tipo_pago
        )
        
        # Convertir a JSON con el encoder personalizado
        json_content = json.loads(
            json.dumps(resultado, cls=DateTimeEncoder)
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=json_content
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/api/marcar-pagada")
async def marcar_solicitud_pagada(
    pago: SolicitudPago,
    current_user: dict = Depends(require_role("pagador"))
):
    """
    Marcar una solicitud como pagada
    
    Requiere rol: pagador
    
    Body:
    - solicitud_id: ID de la solicitud
    - fecha_pago: Fecha del pago (opcional, se usa la actual)
    - referencia_pago: Referencia de la transacción (opcional)
    - comentarios_pagador: Comentarios adicionales (opcional)
    """
    try:
        # Asegurar que el email del pagador sea el del usuario actual
        pago.pagador_email = current_user["email"]
        
        resultado = pagador_controller.marcar_como_pagada(pago)
        
        # Serializar con el encoder personalizado
        json_content = json.dumps(resultado, cls=DateTimeEncoder, ensure_ascii=False)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=json.loads(json_content)
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR en marcar_solicitud_pagada: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al marcar solicitud como pagada: {str(e)}"
        )


@router.post("/api/subir-comprobantes")
async def subir_comprobantes(
    solicitud_id: str = Form(...),
    archivos: List[UploadFile] = File(...),
    current_user: dict = Depends(require_role("pagador"))
):
    """
    Subir comprobantes de pago (sin límite de archivos ni tamaño)
    
    Requiere rol: pagador
    
    Form data:
    - solicitud_id: ID de la solicitud
    - archivos: Array de archivos (sin límite)
    """
    try:
        print(f"\n📎 Subiendo comprobantes para solicitud: {solicitud_id}")
        print(f"📊 Total archivos recibidos: {len(archivos)}")
        
        if not archivos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar al menos un archivo"
            )
        
        # Crear directorio específico para esta solicitud
        solicitud_dir = os.path.join(UPLOAD_DIR, solicitud_id)
        os.makedirs(solicitud_dir, exist_ok=True)
        
        comprobantes_info = []
        
        for archivo in archivos:
            try:
                # Generar nombre único para el archivo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                nombre_archivo = f"{timestamp}_{archivo.filename}"
                ruta_archivo = os.path.join(solicitud_dir, nombre_archivo)
                
                print(f"💾 Guardando: {nombre_archivo}")
                
                # Guardar archivo
                with open(ruta_archivo, "wb") as buffer:
                    shutil.copyfileobj(archivo.file, buffer)
                
                # Obtener tamaño del archivo
                tamaño = os.path.getsize(ruta_archivo)
                
                # Ruta relativa para almacenar en BD
                ruta_relativa = f"/static/uploads/comprobantes/{solicitud_id}/{nombre_archivo}"
                
                comprobante_info = {
                    "nombre": archivo.filename,
                    "nombre_guardado": nombre_archivo,
                    "ruta": ruta_relativa,
                    "tamaño": tamaño,
                    "tipo": archivo.content_type,
                    "fecha_subida": datetime.now().isoformat(),
                    "subido_por": current_user["email"]
                }
                
                comprobantes_info.append(comprobante_info)
                print(f"✅ Archivo guardado: {nombre_archivo} ({tamaño} bytes)")
                
            except Exception as e:
                print(f"❌ Error guardando archivo {archivo.filename}: {str(e)}")
                continue
        
        if not comprobantes_info:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo guardar ningún archivo"
            )
        
        # Registrar comprobantes en la base de datos
        resultado = pagador_controller.subir_comprobantes_pago(
            solicitud_id=solicitud_id,
            comprobantes=comprobantes_info,
            pagador_email=current_user["email"]
        )
        
        print(f"✅ {len(comprobantes_info)} comprobantes subidos y registrados")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": resultado["message"],
                "archivos_subidos": len(comprobantes_info),
                "total_comprobantes": resultado["total_comprobantes"],
                "comprobantes": comprobantes_info
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR en subir_comprobantes: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir comprobantes: {str(e)}"
        )


@router.get("/api/solicitud/{solicitud_id}")
async def get_solicitud_detalle(
    solicitud_id: str,
    current_user: dict = Depends(require_role("pagador"))
):
    """
    Obtener detalles completos de una solicitud
    
    Requiere rol: pagador
    """
    try:
        print(f"\n🔍 GET /api/solicitud/{solicitud_id}")
        
        from pymongo import MongoClient
        import os
        
        # Conectar a MongoDB
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        client = MongoClient(mongo_uri)
        db_name = os.getenv("DATABASE_NAME", "sistema_solicitudes_pagos")
        db = client[db_name]
        
        print(f"📊 Buscando solicitud en base de datos: {db_name}")
        
        solicitud = db["solicitudes_estandar"].find_one({"_id": ObjectId(solicitud_id)})
        
        if not solicitud:
            print(f"❌ Solicitud no encontrada: {solicitud_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud no encontrada"
            )
        
        print(f"✅ Solicitud encontrada: {solicitud.get('folio')}")
        
        # Convertir ObjectId
        solicitud["id"] = str(solicitud["_id"])
        del solicitud["_id"]
        
        # Convertir datetime a string usando el mismo método que otros endpoints
        for campo in ["fecha_creacion", "fecha_envio", "fecha_aprobacion", "fecha_pago", "fecha_limite_comprobante", "created_at", "updated_at"]:
            if campo in solicitud and solicitud[campo]:
                if isinstance(solicitud[campo], datetime):
                    solicitud[campo] = solicitud[campo].isoformat()
        
        # Serializar con DateTimeEncoder
        response_data = {
            "success": True,
            "solicitud": solicitud
        }
        
        json_content = json.dumps(response_data, cls=DateTimeEncoder, ensure_ascii=False)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=json.loads(json_content)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR en get_solicitud_detalle: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener detalles: {str(e)}"
        )
