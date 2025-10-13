"""
Controlador para el Dashboard del Aprobador
Gestiona solicitudes pendientes, aprobaciones y rechazos
"""
from fastapi import HTTPException, status
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv

from app.models.solicitud import (
    SolicitudEstandar,
    SolicitudAprobacion,
    SolicitudRechazo,
    EstadoSolicitud
)

load_dotenv()

# Configuración de MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "sistema_solicitudes_pagos")  # 🔧 CORREGIDO: Usar la BD correcta

class AprobadorController:
    """Controlador para operaciones del aprobador"""
    
    def __init__(self):
        self.mongo_client = MongoClient(MONGO_URI)
        self.db = self.mongo_client[DATABASE_NAME]
        self.solicitudes_collection = self.db["solicitudes_estandar"]
        self.users_collection = self.db["users"]
        
        print(f"🔧 AprobadorController inicializado")
        print(f"   MongoDB URI: {MONGO_URI}")
        print(f"   Database Name: {DATABASE_NAME}")
        print(f"   Colección: solicitudes_estandar")
    
    def get_solicitudes_pendientes(
        self, 
        aprobador_email: str,
        filtro_departamento: Optional[str] = None,
        filtro_tipo_pago: Optional[str] = None,
        limite: int = 100
    ) -> List[Dict]:
        """
        Obtener todas las solicitudes pendientes de aprobación
        
        Args:
            aprobador_email: Email del aprobador
            filtro_departamento: Filtrar por departamento específico
            filtro_tipo_pago: Filtrar por tipo de pago
            limite: Número máximo de solicitudes a retornar
        
        Returns:
            Lista de solicitudes en estado 'enviada' o 'en_revision'
        """
        try:
            # Construir query - SOLO solicitudes enviadas
            query = {
                "estado": "enviada"  # 🔧 Simplificado: solo estado enviada
            }
            
            print(f"🔍 DEBUG - Query inicial: {query}")
            print(f"🔍 DEBUG - Aprobador email: {aprobador_email}")
            
            # Aplicar filtros opcionales
            if filtro_departamento:
                query["departamento"] = filtro_departamento
                print(f"🔍 DEBUG - Filtro departamento aplicado: {filtro_departamento}")
            
            if filtro_tipo_pago:
                query["tipo_pago"] = filtro_tipo_pago
                print(f"🔍 DEBUG - Filtro tipo_pago aplicado: {filtro_tipo_pago}")
            
            print(f"🔍 DEBUG - Query final: {query}")
            
            # Obtener solicitudes ordenadas por fecha de creación (más recientes primero)
            solicitudes = list(
                self.solicitudes_collection.find(query)
                .sort("fecha_creacion", -1)
                .limit(limite)
            )
            
            print(f"🔍 DEBUG - Solicitudes encontradas en DB: {len(solicitudes)}")
            
            # Convertir ObjectId a string y formatear datos
            result = []
            for i, solicitud in enumerate(solicitudes, 1):
                print(f"  📄 Procesando solicitud {i}/{len(solicitudes)}: {str(solicitud['_id'])}")
            for i, solicitud in enumerate(solicitudes, 1):
                print(f"  📄 Procesando solicitud {i}/{len(solicitudes)}: {str(solicitud['_id'])}")
                
                try:
                    # Obtener información del solicitante
                    solicitante_email = solicitud.get("solicitante_email")
                    print(f"     Email solicitante: {solicitante_email}")
                    
                    solicitante = None
                    if solicitante_email:
                        solicitante = self.users_collection.find_one(
                            {"email": solicitante_email}
                        )
                        print(f"     Solicitante encontrado: {solicitante is not None}")
                    
                    # Construir nombre del solicitante de forma segura
                    if solicitante:
                        first_name = solicitante.get('first_name', '')
                        last_name = solicitante.get('last_name', '')
                        nombre_completo = f"{first_name} {last_name}".strip() or "N/A"
                    else:
                        nombre_completo = "N/A"
                    
                    # Función auxiliar para convertir fechas a string
                    def fecha_a_string(fecha):
                        if fecha is None:
                            return None
                        if isinstance(fecha, datetime):
                            return fecha.isoformat()
                        return str(fecha)
                    
                    solicitud_dict = {
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
                        "archivos_adjuntos": solicitud.get("archivos_adjuntos", []),
                        
                        # Información del solicitante
                        "solicitante": {
                            "email": solicitante_email or "N/A",
                            "nombre": nombre_completo,
                            "department": solicitante.get("department", "N/A") if solicitante else "N/A"
                        }
                    }
                    
                    result.append(solicitud_dict)
                    print(f"     ✅ Solicitud procesada correctamente")
                    
                except Exception as e:
                    print(f"     ❌ Error procesando solicitud: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    # Continuar con la siguiente solicitud
                    continue
            
            print(f"✅ DEBUG - Total solicitudes procesadas: {len(result)}")
            
            return result
            
        except Exception as e:
            print(f"❌ DEBUG - Error en get_solicitudes_pendientes: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener solicitudes pendientes: {str(e)}"
            )
    
    def aprobar_solicitud(self, aprobacion: SolicitudAprobacion) -> Dict:
        """
        Aprobar una solicitud
        
        Args:
            aprobacion: Datos de la aprobación
        
        Returns:
            Solicitud actualizada
        """
        try:
            # Validar que la solicitud existe y está en estado correcto
            solicitud = self.solicitudes_collection.find_one({
                "_id": ObjectId(aprobacion.solicitud_id)
            })
            
            if not solicitud:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Solicitud no encontrada"
                )
            
            estado_actual = solicitud.get("estado")
            if estado_actual not in [
                EstadoSolicitud.ENVIADA.value,
                EstadoSolicitud.EN_REVISION.value
            ]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No se puede aprobar una solicitud en estado '{estado_actual}'"
                )
            
            # Validar que el aprobador tiene permisos
            aprobador = self.users_collection.find_one({
                "email": aprobacion.aprobador_email
            })
            
            if not aprobador or aprobador.get("role") != "aprobador":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Usuario no autorizado para aprobar solicitudes"
                )
            
            # Actualizar la solicitud
            update_data = {
                "estado": EstadoSolicitud.APROBADA.value,
                "comentarios_aprobador": aprobacion.comentarios_aprobador,
                "aprobador_email": aprobacion.aprobador_email,
                "fecha_aprobacion": datetime.utcnow(),
                "fecha_actualizacion": datetime.utcnow()
            }
            
            result = self.solicitudes_collection.update_one(
                {"_id": ObjectId(aprobacion.solicitud_id)},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No se pudo actualizar la solicitud"
                )
            
            return {
                "success": True,
                "message": "Solicitud aprobada exitosamente",
                "solicitud_id": aprobacion.solicitud_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al aprobar solicitud: {str(e)}"
            )
    
    def rechazar_solicitud(self, rechazo: SolicitudRechazo) -> Dict:
        """
        Rechazar una solicitud (requiere comentarios obligatorios)
        
        Args:
            rechazo: Datos del rechazo con comentarios obligatorios
        
        Returns:
            Solicitud actualizada
        """
        try:
            # Validar que la solicitud existe y está en estado correcto
            solicitud = self.solicitudes_collection.find_one({
                "_id": ObjectId(rechazo.solicitud_id)
            })
            
            if not solicitud:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Solicitud no encontrada"
                )
            
            estado_actual = solicitud.get("estado")
            if estado_actual not in [
                EstadoSolicitud.ENVIADA.value,
                EstadoSolicitud.EN_REVISION.value
            ]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No se puede rechazar una solicitud en estado '{estado_actual}'"
                )
            
            # Validar que el aprobador tiene permisos
            aprobador = self.users_collection.find_one({
                "email": rechazo.aprobador_email
            })
            
            if not aprobador or aprobador.get("role") != "aprobador":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Usuario no autorizado para rechazar solicitudes"
                )
            
            # Validar que hay comentarios (validación adicional)
            if not rechazo.comentarios_aprobador or len(rechazo.comentarios_aprobador.strip()) < 10:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Debe proporcionar un comentario detallado (mínimo 10 caracteres) explicando el motivo del rechazo"
                )
            
            # Actualizar la solicitud
            update_data = {
                "estado": EstadoSolicitud.RECHAZADA.value,
                "comentarios_aprobador": rechazo.comentarios_aprobador,
                "aprobador_email": rechazo.aprobador_email,
                "fecha_rechazo": datetime.utcnow(),
                "fecha_actualizacion": datetime.utcnow()
            }
            
            result = self.solicitudes_collection.update_one(
                {"_id": ObjectId(rechazo.solicitud_id)},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No se pudo actualizar la solicitud"
                )
            
            return {
                "success": True,
                "message": "Solicitud rechazada exitosamente",
                "solicitud_id": rechazo.solicitud_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al rechazar solicitud: {str(e)}"
            )
    
    def get_estadisticas_aprobador(self, aprobador_email: str) -> Dict:
        """
        Obtener estadísticas del dashboard del aprobador
        
        Args:
            aprobador_email: Email del aprobador
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            # Total de solicitudes pendientes
            pendientes = self.solicitudes_collection.count_documents({
                "estado": {
                    "$in": [
                        EstadoSolicitud.ENVIADA.value,
                        EstadoSolicitud.EN_REVISION.value
                    ]
                }
            })
            
            # Total aprobadas por este aprobador
            aprobadas = self.solicitudes_collection.count_documents({
                "aprobador_email": aprobador_email,
                "estado": EstadoSolicitud.APROBADA.value
            })
            
            # Total rechazadas por este aprobador
            rechazadas = self.solicitudes_collection.count_documents({
                "aprobador_email": aprobador_email,
                "estado": EstadoSolicitud.RECHAZADA.value
            })
            
            # Monto total de solicitudes pendientes
            pipeline_monto_pendiente = [
                {
                    "$match": {
                        "estado": {
                            "$in": [
                                EstadoSolicitud.ENVIADA.value,
                                EstadoSolicitud.EN_REVISION.value
                            ]
                        }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$monto"}
                    }
                }
            ]
            
            resultado_monto = list(self.solicitudes_collection.aggregate(pipeline_monto_pendiente))
            monto_pendiente = resultado_monto[0]["total"] if resultado_monto else 0
            
            return {
                "pendientes": pendientes,
                "aprobadas": aprobadas,
                "rechazadas": rechazadas,
                "monto_pendiente": round(monto_pendiente, 2),
                "total_procesadas": aprobadas + rechazadas
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener estadísticas: {str(e)}"
            )
    
    def get_historial_aprobador(
        self,
        aprobador_email: str,
        filtro_estado: Optional[str] = None,
        filtro_departamento: Optional[str] = None,
        filtro_tipo_pago: Optional[str] = None,
        limite: int = 100
    ) -> List[Dict]:
        """
        Obtener el historial de solicitudes aprobadas y rechazadas por el aprobador
        
        Args:
            aprobador_email: Email del aprobador
            filtro_estado: Filtrar por estado específico (aprobada/rechazada)
            filtro_departamento: Filtrar por departamento
            filtro_tipo_pago: Filtrar por tipo de pago
            limite: Número máximo de solicitudes a retornar
            
        Returns:
            Lista de solicitudes procesadas por el aprobador
        """
        try:
            print(f"\n{'='*80}")
            print(f"📋 HISTORIAL DEL APROBADOR: {aprobador_email}")
            print(f"{'='*80}")
            
            # Construir query
            query = {
                "aprobador_email": aprobador_email,
                "estado": {"$in": ["aprobada", "rechazada", "pagada"]}  # Incluir pagada para ver el ciclo completo
            }
            
            if filtro_estado:
                query["estado"] = filtro_estado
                print(f"🔍 Filtro estado: {filtro_estado}")
            
            if filtro_departamento:
                query["departamento"] = filtro_departamento
                print(f"🔍 Filtro departamento: {filtro_departamento}")
            
            if filtro_tipo_pago:
                query["tipo_pago"] = filtro_tipo_pago
                print(f"🔍 Filtro tipo pago: {filtro_tipo_pago}")
            
            print(f"🔎 Query: {query}")
            
            # Buscar solicitudes ordenadas por fecha de aprobación (más recientes primero)
            solicitudes = list(
                self.solicitudes_collection
                .find(query)
                .sort("fecha_aprobacion", -1)
                .limit(limite)
            )
            
            print(f"📊 Solicitudes encontradas en historial: {len(solicitudes)}")
            
            resultado = []
            
            for solicitud in solicitudes:
                try:
                    print(f"   📄 Procesando solicitud ID: {solicitud.get('_id')}")
                    
                    # Obtener información del solicitante
                    solicitante_email = solicitud.get("solicitante_email", "N/A")
                    solicitante = None
                    if solicitante_email != "N/A":
                        solicitante = self.users_collection.find_one({"email": solicitante_email})
                    
                    # Construir nombre del solicitante
                    if solicitante:
                        nombre_completo = f"{solicitante.get('first_name', '')} {solicitante.get('last_name', '')}".strip() or "N/A"
                    else:
                        nombre_completo = "N/A"
                    
                    # Función auxiliar para convertir fechas a string
                    def fecha_a_string(fecha):
                        if fecha is None:
                            return None
                        if isinstance(fecha, datetime):
                            return fecha.isoformat()
                        return str(fecha)
                    
                    # Generar folio si no existe
                    folio = solicitud.get("folio", f"SOL-{str(solicitud['_id'])[:8].upper()}")
                    
                    solicitud_dict = {
                        "id": str(solicitud["_id"]),
                        "folio": folio,
                        "departamento": solicitud.get("departamento", "N/A"),
                        "monto": solicitud.get("monto", 0),
                        "tipo_moneda": solicitud.get("tipo_moneda", "N/A"),
                        "banco_destino": solicitud.get("banco_destino", "N/A"),
                        "cuenta_destino": solicitud.get("cuenta_destino", "N/A"),
                        "es_clabe": solicitud.get("es_clabe", False),
                        "nombre_beneficiario": solicitud.get("nombre_beneficiario", "N/A"),
                        "segundo_beneficiario": solicitud.get("segundo_beneficiario"),
                        "nombre_empresa": solicitud.get("nombre_empresa"),
                        "tipo_pago": solicitud.get("tipo_pago", "N/A"),
                        "concepto_pago": solicitud.get("concepto_pago", "N/A"),
                        "concepto_otros": solicitud.get("concepto_otros"),
                        "fecha_limite_pago": fecha_a_string(solicitud.get("fecha_limite_pago")),
                        "descripcion_tipo_pago": solicitud.get("descripcion_tipo_pago", ""),
                        "estado": solicitud.get("estado", "N/A"),
                        "fecha_creacion": fecha_a_string(solicitud.get("fecha_creacion")),
                        "fecha_actualizacion": fecha_a_string(solicitud.get("fecha_actualizacion")),
                        "fecha_aprobacion": fecha_a_string(solicitud.get("fecha_aprobacion")),
                        "fecha_pago": fecha_a_string(solicitud.get("fecha_pago")),
                        "comentarios_solicitante": solicitud.get("comentarios_solicitante", ""),
                        "comentarios_aprobador": solicitud.get("comentarios_aprobador", ""),
                        "comentarios_pagador": solicitud.get("comentarios_pagador", ""),
                        "aprobador_email": solicitud.get("aprobador_email", "N/A"),
                        "pagador_email": solicitud.get("pagador_email"),
                        "referencia_pago": solicitud.get("referencia_pago"),
                        "archivos_adjuntos": solicitud.get("archivos_adjuntos", []),
                        "comprobantes_pago": solicitud.get("comprobantes_pago", []),
                        
                        # Información del solicitante
                        "solicitante": {
                            "email": solicitante_email,
                            "nombre": nombre_completo,
                            "department": solicitante.get("department", "N/A") if solicitante else "N/A"
                        }
                    }
                    
                    resultado.append(solicitud_dict)
                    print(f"      ✅ Solicitud procesada: {folio} - Estado: {solicitud_dict['estado']}")
                    
                except Exception as e:
                    print(f"      ❌ Error procesando solicitud {solicitud.get('_id')}: {str(e)}")
                    continue
            
            print(f"✅ Total solicitudes en historial: {len(resultado)}\n")
            return resultado
            
        except Exception as e:
            print(f"❌ ERROR en get_historial_aprobador: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener historial: {str(e)}"
            )
    
    def __del__(self):
        """Cerrar conexión al destruir el objeto"""
        if hasattr(self, 'mongo_client'):
            self.mongo_client.close()
