"""
Rutas API para el Dashboard del Aprobador
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.requests import Request
from typing import Optional
import json
from datetime import datetime
from bson import ObjectId

from app.controllers.aprobador_controller import AprobadorController
from app.models.solicitud import SolicitudAprobacion, SolicitudRechazo
from app.middleware.auth_middleware import get_current_user, require_role, require_any_role

router = APIRouter(prefix="/aprobador", tags=["Aprobador"])

# Instancia del controlador
aprobador_controller = AprobadorController()


# Encoder JSON personalizado para manejar datetime y ObjectId
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_aprobador(
    request: Request,
    current_user: dict = Depends(require_any_role("aprobador", "admin"))
):
    """
    Página principal del dashboard del aprobador
    """
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
    
    return templates.TemplateResponse(
        "dashboards/aprobador.html",
        {
            "request": request,
            "user": current_user,
            "title": "Dashboard Aprobador"
        }
    )


@router.get("/api/solicitudes-pendientes")
async def get_solicitudes_pendientes(
    filtro_departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    filtro_tipo_pago: Optional[str] = Query(None, description="Filtrar por tipo de pago"),
    limite: int = Query(100, ge=1, le=500, description="Límite de resultados"),
    current_user: dict = Depends(require_any_role("aprobador", "admin"))
):
    """
    Obtener todas las solicitudes pendientes de aprobación
    
    Requiere rol: aprobador
    """
    try:
        solicitudes = aprobador_controller.get_solicitudes_pendientes(
            aprobador_email=current_user["email"],
            filtro_departamento=filtro_departamento,
            filtro_tipo_pago=filtro_tipo_pago,
            limite=limite
        )
        
        print(f"📤 Intentando devolver {len(solicitudes)} solicitudes")
        
        response_data = {
            "success": True,
            "total": len(solicitudes),
            "solicitudes": solicitudes
        }
        
        print(f"✅ Response data construido correctamente")
        
        # Usar el encoder personalizado para serializar correctamente
        json_content = json.dumps(response_data, cls=DateTimeEncoder, ensure_ascii=False)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=json.loads(json_content)  # Convertir de nuevo a dict para JSONResponse
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERROR en get_solicitudes_pendientes endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener solicitudes: {str(e)}"
        )


@router.get("/api/estadisticas")
async def get_estadisticas(
    current_user: dict = Depends(require_any_role("aprobador", "admin"))
):
    """
    Obtener estadísticas del dashboard
    
    Requiere rol: aprobador
    """
    try:
        estadisticas = aprobador_controller.get_estadisticas_aprobador(
            aprobador_email=current_user["email"]
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "estadisticas": estadisticas
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.get("/api/historial")
async def get_historial(
    filtro_estado: Optional[str] = Query(None, description="Filtrar por estado: aprobada, rechazada, pagada"),
    filtro_departamento: Optional[str] = Query(None, description="Filtrar por departamento"),
    filtro_tipo_pago: Optional[str] = Query(None, description="Filtrar por tipo de pago"),
    limite: int = Query(100, description="Límite de solicitudes"),
    current_user: dict = Depends(require_any_role("aprobador", "admin"))
):
    """
    Obtener historial de solicitudes aprobadas y rechazadas por el aprobador
    
    Requiere rol: aprobador
    
    Query params:
    - filtro_estado: Filtrar por estado específico (aprobada/rechazada/pagada)
    - filtro_departamento: Filtrar por departamento
    - filtro_tipo_pago: Filtrar por tipo de pago
    - limite: Número máximo de solicitudes (default 100)
    """
    try:
        print(f"\n🔍 GET /aprobador/api/historial")
        print(f"   Usuario: {current_user['email']}")
        print(f"   Filtros: estado={filtro_estado}, depto={filtro_departamento}, tipo={filtro_tipo_pago}")
        
        solicitudes = aprobador_controller.get_historial_aprobador(
            aprobador_email=current_user["email"],
            filtro_estado=filtro_estado,
            filtro_departamento=filtro_departamento,
            filtro_tipo_pago=filtro_tipo_pago,
            limite=limite
        )
        
        # Usar el encoder personalizado para manejar fechas
        json_content = json.dumps({
            "success": True,
            "total": len(solicitudes),
            "solicitudes": solicitudes
        }, cls=DateTimeEncoder, ensure_ascii=False)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=json.loads(json_content)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error en get_historial: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener historial: {str(e)}"
        )


@router.post("/api/aprobar")
async def aprobar_solicitud(
    aprobacion: SolicitudAprobacion,
    current_user: dict = Depends(require_any_role("aprobador", "admin"))
):
    """
    Aprobar una solicitud
    
    Requiere rol: aprobador
    
    Body:
    - solicitud_id: ID de la solicitud
    - comentarios_aprobador: Comentarios opcionales
    """
    try:
        # Asegurar que el email del aprobador sea el del usuario actual
        aprobacion.aprobador_email = current_user["email"]
        
        resultado = aprobador_controller.aprobar_solicitud(aprobacion)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=resultado
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al aprobar solicitud: {str(e)}"
        )


@router.post("/api/rechazar")
async def rechazar_solicitud(
    rechazo: SolicitudRechazo,
    current_user: dict = Depends(require_any_role("aprobador", "admin"))
):
    """
    Rechazar una solicitud (requiere comentarios obligatorios)
    
    Requiere rol: aprobador
    
    Body:
    - solicitud_id: ID de la solicitud
    - comentarios_aprobador: Comentarios OBLIGATORIOS (min 10 caracteres)
    """
    try:
        # Asegurar que el email del aprobador sea el del usuario actual
        rechazo.aprobador_email = current_user["email"]
        
        resultado = aprobador_controller.rechazar_solicitud(rechazo)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=resultado
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al rechazar solicitud: {str(e)}"
        )


@router.get("/api/solicitud/{solicitud_id}")
async def get_solicitud_detalle(
    solicitud_id: str,
    current_user: dict = Depends(require_any_role("aprobador", "admin"))
):
    """
    Obtener detalles de una solicitud específica
    
    Requiere rol: aprobador
    """
    try:
        print(f"🔍 Obteniendo detalles de solicitud: {solicitud_id}")
        
        # Usar el controlador existente para obtener la solicitud
        from pymongo import MongoClient
        import os
        
        # Usar la misma configuración que el controlador
        mongo_client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
        db = mongo_client[os.getenv("DATABASE_NAME", "sistema_solicitudes_pagos")]  # 🔧 BD correcta
        
        solicitud = db["solicitudes_estandar"].find_one({"_id": ObjectId(solicitud_id)})
        
        if not solicitud:
            print(f"❌ Solicitud no encontrada: {solicitud_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud no encontrada"
            )
        
        print(f"✅ Solicitud encontrada")
        
        # Obtener información del solicitante
        solicitante_email = solicitud.get("solicitante_email")
        solicitante = None
        if solicitante_email:
            solicitante = db["users"].find_one({"email": solicitante_email})
        
        # Construir respuesta con toda la información
        def fecha_a_string(fecha):
            if fecha is None:
                return None
            if isinstance(fecha, datetime):
                return fecha.isoformat()
            return str(fecha)
        
        solicitud_detalle = {
            "id": str(solicitud["_id"]),
            "departamento": solicitud.get("departamento", "N/A"),
            "monto": solicitud.get("monto", 0),
            "tipo_moneda": solicitud.get("tipo_moneda", "N/A"),
            "banco_destino": solicitud.get("banco_destino", "N/A"),
            "cuenta_destino": solicitud.get("cuenta_destino", "N/A"),
            "nombre_beneficiario": solicitud.get("nombre_beneficiario", "N/A"),
            "nombre_empresa": solicitud.get("nombre_empresa", "N/A"),
            "tipo_pago": solicitud.get("tipo_pago", "N/A"),
            "concepto_pago": solicitud.get("concepto_pago", "N/A"),
            "concepto_otros": solicitud.get("concepto_otros", ""),
            "fecha_limite_pago": fecha_a_string(solicitud.get("fecha_limite_pago")),
            "descripcion_tipo_pago": solicitud.get("descripcion_tipo_pago", ""),
            "estado": solicitud.get("estado", "N/A"),
            "fecha_creacion": fecha_a_string(solicitud.get("fecha_creacion")),
            "fecha_actualizacion": fecha_a_string(solicitud.get("fecha_actualizacion")),
            "comentarios_solicitante": solicitud.get("comentarios_solicitante", ""),
            "comentarios_aprobador": solicitud.get("comentarios_aprobador", ""),
            "archivos_adjuntos": solicitud.get("archivos_adjuntos", []),
            "solicitante": {
                "email": solicitante_email or "N/A",
                "nombre": f"{solicitante.get('first_name', '')} {solicitante.get('last_name', '')}".strip() if solicitante else "N/A",
                "department": solicitante.get("department", "N/A") if solicitante else "N/A"
            }
        }
        
        # Usar el encoder personalizado
        json_content = json.dumps({
            "success": True,
            "solicitud": solicitud_detalle
        }, cls=DateTimeEncoder, ensure_ascii=False)
        
        print(f"✅ Detalles construidos correctamente")
        
        mongo_client.close()
        
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
            detail=f"Error al obtener solicitud: {str(e)}"
        )
