"""
Controller para las operaciones del rol Pagador
"""
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo import MongoClient
import os
from typing import Optional, List

from app.models.solicitud import SolicitudPago


class PagadorController:
    def __init__(self, database_name: str = None):
        """
        Inicializar controlador del Pagador
        """
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(mongo_uri)
        
        # Usar el nombre de base de datos proporcionado o el de la variable de entorno
        db_name = database_name or os.getenv("DATABASE_NAME", "sistema_solicitudes_pagos")
        self.db = self.client[db_name]
        
        self.solicitudes_collection = self.db["solicitudes_estandar"]
        self.users_collection = self.db["users"]
    
    def get_solicitudes_aprobadas(
        self,
        pagador_email: str,
        filtro_departamento: Optional[str] = None,
        filtro_tipo_pago: Optional[str] = None
    ) -> dict:
        """
        Obtener todas las solicitudes aprobadas (listas para pagar)
        
        Args:
            pagador_email: Email del pagador actual
            filtro_departamento: Filtro opcional por departamento
            filtro_tipo_pago: Filtro opcional por tipo de pago
            
        Returns:
            Diccionario con solicitudes y metadatos
        """
        print(f"\n{'='*60}")
        print(f"🔍 Obteniendo solicitudes aprobadas para pagador: {pagador_email}")
        print(f"{'='*60}")
        
        try:
            # Construir query - solo solicitudes aprobadas
            query = {"estado": "aprobada"}
            
            if filtro_departamento:
                query["departamento"] = filtro_departamento
                print(f"📌 Filtro departamento: {filtro_departamento}")
            
            if filtro_tipo_pago:
                query["tipo_pago"] = filtro_tipo_pago
                print(f"📌 Filtro tipo pago: {filtro_tipo_pago}")
            
            print(f"🔎 Query MongoDB: {query}")
            
            # Buscar solicitudes
            solicitudes_cursor = self.solicitudes_collection.find(query).sort("fecha_aprobacion", -1)
            solicitudes = list(solicitudes_cursor)
            
            print(f"📊 Total solicitudes encontradas: {len(solicitudes)}")
            
            # Procesar cada solicitud
            solicitudes_procesadas = []
            for sol in solicitudes:
                try:
                    # Calcular días restantes para subir comprobante (3 días hábiles desde aprobación)
                    dias_restantes = None
                    if sol.get("estado") == "pagada" and sol.get("fecha_pago"):
                        fecha_pago = sol.get("fecha_pago")
                        if isinstance(fecha_pago, str):
                            try:
                                fecha_pago = datetime.fromisoformat(fecha_pago.replace('Z', '+00:00'))
                            except:
                                fecha_pago = datetime.now()
                        
                        # Calcular fecha límite (3 días hábiles)
                        fecha_limite = self._calcular_fecha_limite(fecha_pago, 3)
                        dias_restantes = (fecha_limite - datetime.now()).days
                    
                    # Generar folio si no existe
                    folio = sol.get("folio", f"SOL-{str(sol['_id'])[:8].upper()}")
                    
                    # Construir diccionario con los campos REALES de la base de datos
                    solicitud_dict = {
                        "id": str(sol["_id"]),
                        "folio": folio,
                        "tipo_pago": sol.get("tipo_pago", "N/A"),
                        "concepto_pago": sol.get("concepto_pago", "N/A"),
                        "concepto_otros": sol.get("concepto_otros"),
                        "descripcion_tipo_pago": sol.get("descripcion_tipo_pago", ""),
                        "monto": float(sol.get("monto", 0)),
                        "tipo_moneda": sol.get("tipo_moneda", "MXN"),
                        "departamento": sol.get("departamento", "N/A"),
                        "solicitante_email": sol.get("solicitante_email", "N/A"),
                        "nombre_beneficiario": sol.get("nombre_beneficiario", "N/A"),
                        "segundo_beneficiario": sol.get("segundo_beneficiario"),
                        "nombre_empresa": sol.get("nombre_empresa"),
                        "banco_destino": sol.get("banco_destino", "N/A"),
                        "cuenta_destino": sol.get("cuenta_destino", "N/A"),
                        "es_clabe": sol.get("es_clabe", False),
                        "estado": sol.get("estado", "aprobada"),
                        "fecha_creacion": sol.get("fecha_creacion").isoformat() if sol.get("fecha_creacion") else None,
                        "fecha_aprobacion": sol.get("fecha_aprobacion").isoformat() if sol.get("fecha_aprobacion") else None,
                        "fecha_limite_pago": sol.get("fecha_limite_pago").isoformat() if sol.get("fecha_limite_pago") else None,
                        "fecha_pago": sol.get("fecha_pago").isoformat() if sol.get("fecha_pago") else None,
                        "aprobador_email": sol.get("aprobador_email", "N/A"),
                        "comentarios_aprobador": sol.get("comentarios_aprobador", ""),
                        "comentarios_solicitante": sol.get("comentarios_solicitante", ""),
                        "pagador_email": sol.get("pagador_email"),
                        "referencia_pago": sol.get("referencia_pago"),
                        "comentarios_pagador": sol.get("comentarios_pagador"),
                        "comprobantes_pago": sol.get("comprobantes_pago", []),
                        "dias_restantes_comprobante": dias_restantes,
                        "archivos_adjuntos": sol.get("archivos_adjuntos", [])
                    }
                    
                    solicitudes_procesadas.append(solicitud_dict)
                    print(f"✅ Solicitud procesada: {solicitud_dict['folio']} - {solicitud_dict['nombre_beneficiario']}")
                    
                except Exception as e:
                    print(f"❌ Error procesando solicitud {sol.get('_id')}: {str(e)}")
                    continue
            
            resultado = {
                "success": True,
                "total": len(solicitudes_procesadas),
                "solicitudes": solicitudes_procesadas
            }
            
            print(f"✅ Resultado final: {resultado['total']} solicitudes")
            return resultado
            
        except Exception as e:
            print(f"❌ ERROR en get_solicitudes_aprobadas: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _calcular_fecha_limite(self, fecha_inicio: datetime, dias_habiles: int) -> datetime:
        """
        Calcular fecha límite agregando días hábiles (lunes a viernes)
        
        Args:
            fecha_inicio: Fecha de inicio
            dias_habiles: Número de días hábiles a agregar
            
        Returns:
            Fecha límite
        """
        fecha_actual = fecha_inicio
        dias_agregados = 0
        
        while dias_agregados < dias_habiles:
            fecha_actual += timedelta(days=1)
            # 0 = Lunes, 6 = Domingo
            if fecha_actual.weekday() < 5:  # Lunes a Viernes
                dias_agregados += 1
        
        return fecha_actual
    
    def marcar_como_pagada(self, pago: SolicitudPago) -> dict:
        """
        Marcar una solicitud como pagada
        
        Args:
            pago: Datos del pago
            
        Returns:
            Diccionario con resultado de la operación
        """
        print(f"\n{'='*60}")
        print(f"💰 Marcando solicitud como pagada: {pago.solicitud_id}")
        print(f"{'='*60}")
        
        try:
            # Validar que existe la solicitud
            solicitud = self.solicitudes_collection.find_one({
                "_id": ObjectId(pago.solicitud_id)
            })
            
            if not solicitud:
                print(f"❌ Solicitud no encontrada")
                raise ValueError("Solicitud no encontrada")
            
            # Validar que está aprobada
            if solicitud.get("estado") != "aprobada":
                print(f"❌ Solicitud no está en estado aprobada: {solicitud.get('estado')}")
                raise ValueError(f"La solicitud debe estar aprobada. Estado actual: {solicitud.get('estado')}")
            
            # Preparar actualización
            fecha_pago = pago.fecha_pago or datetime.now()
            
            update_data = {
                "estado": "pagada",
                "fecha_pago": fecha_pago,
                "pagador_email": pago.pagador_email,
                "updated_at": datetime.now()
            }
            
            # Agregar campos opcionales si existen
            if pago.referencia_pago:
                update_data["referencia_pago"] = pago.referencia_pago
            
            if pago.comentarios_pagador:
                update_data["comentarios_pagador"] = pago.comentarios_pagador
            
            # Calcular fecha límite para subir comprobante
            fecha_limite = self._calcular_fecha_limite(fecha_pago, 3)
            update_data["fecha_limite_comprobante"] = fecha_limite
            
            print(f"📝 Datos a actualizar: {update_data}")
            
            # Actualizar en MongoDB
            result = self.solicitudes_collection.update_one(
                {"_id": ObjectId(pago.solicitud_id)},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                print(f"⚠️ No se modificó ningún documento")
                raise ValueError("No se pudo actualizar la solicitud")
            
            print(f"✅ Solicitud marcada como pagada exitosamente")
            
            # Obtener solicitud actualizada
            solicitud_actualizada = self.solicitudes_collection.find_one({
                "_id": ObjectId(pago.solicitud_id)
            })
            
            # Convertir fechas a string para JSON
            if solicitud_actualizada:
                for campo in ["fecha_creacion", "fecha_envio", "fecha_aprobacion", "fecha_pago", "fecha_limite_comprobante", "updated_at", "created_at"]:
                    if campo in solicitud_actualizada and solicitud_actualizada[campo]:
                        if isinstance(solicitud_actualizada[campo], datetime):
                            solicitud_actualizada[campo] = solicitud_actualizada[campo].isoformat()
                
                solicitud_actualizada["id"] = str(solicitud_actualizada["_id"])
                del solicitud_actualizada["_id"]
            
            return {
                "success": True,
                "message": "Solicitud marcada como pagada exitosamente",
                "solicitud": solicitud_actualizada,
                "fecha_limite_comprobante": fecha_limite.isoformat()
            }
            
        except ValueError as ve:
            print(f"❌ Error de validación: {str(ve)}")
            raise
        except Exception as e:
            print(f"❌ ERROR en marcar_como_pagada: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def subir_comprobantes_pago(
        self,
        solicitud_id: str,
        comprobantes: List[dict],
        pagador_email: str
    ) -> dict:
        """
        Registrar comprobantes de pago subidos
        
        Args:
            solicitud_id: ID de la solicitud
            comprobantes: Lista de diccionarios con info de archivos
            pagador_email: Email del pagador
            
        Returns:
            Diccionario con resultado
        """
        print(f"\n{'='*60}")
        print(f"📎 Subiendo comprobantes para solicitud: {solicitud_id}")
        print(f"📊 Total comprobantes: {len(comprobantes)}")
        print(f"{'='*60}")
        
        try:
            # Validar que existe la solicitud
            solicitud = self.solicitudes_collection.find_one({
                "_id": ObjectId(solicitud_id)
            })
            
            if not solicitud:
                raise ValueError("Solicitud no encontrada")
            
            # Validar que está pagada
            if solicitud.get("estado") != "pagada":
                raise ValueError("La solicitud debe estar marcada como pagada para subir comprobantes")
            
            # Agregar comprobantes al array existente
            comprobantes_actuales = solicitud.get("comprobantes_pago", [])
            comprobantes_actuales.extend(comprobantes)
            
            # Actualizar en MongoDB
            result = self.solicitudes_collection.update_one(
                {"_id": ObjectId(solicitud_id)},
                {
                    "$set": {
                        "comprobantes_pago": comprobantes_actuales,
                        "updated_at": datetime.now()
                    }
                }
            )
            
            if result.modified_count == 0:
                raise ValueError("No se pudo actualizar los comprobantes")
            
            print(f"✅ {len(comprobantes)} comprobantes subidos exitosamente")
            
            return {
                "success": True,
                "message": f"{len(comprobantes)} comprobantes subidos exitosamente",
                "total_comprobantes": len(comprobantes_actuales)
            }
            
        except Exception as e:
            print(f"❌ ERROR en subir_comprobantes_pago: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_estadisticas_pagador(self, pagador_email: str) -> dict:
        """
        Obtener estadísticas para el dashboard del pagador
        
        Args:
            pagador_email: Email del pagador
            
        Returns:
            Diccionario con estadísticas
        """
        try:
            # Solicitudes aprobadas (pendientes de pago)
            aprobadas = self.solicitudes_collection.count_documents({"estado": "aprobada"})
            
            # Solicitudes pagadas
            pagadas = self.solicitudes_collection.count_documents({"estado": "pagada"})
            
            # Solicitudes pagadas este mes
            primer_dia_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            pagadas_mes = self.solicitudes_collection.count_documents({
                "estado": "pagada",
                "fecha_pago": {"$gte": primer_dia_mes}
            })
            
            # Monto total pagado este mes
            pipeline = [
                {
                    "$match": {
                        "estado": "pagada",
                        "fecha_pago": {"$gte": primer_dia_mes}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$monto_total"}
                    }
                }
            ]
            
            result = list(self.solicitudes_collection.aggregate(pipeline))
            monto_pagado_mes = result[0]["total"] if result else 0
            
            # Solicitudes con comprobantes pendientes
            comprobantes_pendientes = self.solicitudes_collection.count_documents({
                "estado": "pagada",
                "$or": [
                    {"comprobantes_pago": {"$exists": False}},
                    {"comprobantes_pago": {"$size": 0}}
                ]
            })
            
            estadisticas = {
                "pendientes_pago": aprobadas,
                "pagadas_total": pagadas,
                "pagadas_mes": pagadas_mes,
                "monto_pagado_mes": float(monto_pagado_mes),
                "comprobantes_pendientes": comprobantes_pendientes
            }
            
            print(f"📊 Estadísticas pagador: {estadisticas}")
            
            return estadisticas
            
        except Exception as e:
            print(f"❌ ERROR en get_estadisticas_pagador: {str(e)}")
            raise
    
    def get_historial_pagador(
        self,
        pagador_email: str,
        filtro_estado: Optional[str] = None,
        filtro_departamento: Optional[str] = None,
        filtro_tipo_pago: Optional[str] = None
    ) -> dict:
        """
        Obtener el historial de solicitudes procesadas por el pagador (pagadas)
        
        Args:
            pagador_email: Email del pagador actual
            filtro_estado: Filtro opcional por estado (solo 'pagada' aplica)
            filtro_departamento: Filtro opcional por departamento
            filtro_tipo_pago: Filtro opcional por tipo de pago
            
        Returns:
            Diccionario con solicitudes procesadas y metadatos
        """
        print(f"\n{'='*60}")
        print(f"📜 Obteniendo historial del pagador: {pagador_email}")
        print(f"{'='*60}")
        
        try:
            # Construir query - solo solicitudes pagadas
            query = {
                "pagador_email": pagador_email,
                "estado": "pagada"
            }
            
            # Aplicar filtros opcionales
            if filtro_departamento and filtro_departamento != "todos":
                query["departamento"] = filtro_departamento
                print(f"🏢 Filtro departamento: {filtro_departamento}")
            
            if filtro_tipo_pago and filtro_tipo_pago != "todos":
                query["tipo_pago"] = filtro_tipo_pago
                print(f"💳 Filtro tipo de pago: {filtro_tipo_pago}")
            
            print(f"🔎 Query: {query}")
            
            # Obtener solicitudes ordenadas por fecha de pago (más reciente primero)
            cursor = self.solicitudes_collection.find(query).sort("fecha_pago", -1)
            solicitudes = list(cursor)
            
            print(f"📊 Total de solicitudes en historial: {len(solicitudes)}")
            
            # Procesar solicitudes
            solicitudes_procesadas = []
            for sol in solicitudes:
                try:
                    # Convertir ObjectId a string
                    sol['id'] = str(sol['_id'])
                    
                    # Calcular días desde el pago
                    if sol.get('fecha_pago'):
                        dias_desde_pago = (datetime.utcnow() - sol['fecha_pago']).days
                        sol['dias_desde_pago'] = dias_desde_pago
                    
                    solicitudes_procesadas.append(sol)
                    
                except Exception as e:
                    print(f"⚠️ Error procesando solicitud {sol.get('_id')}: {str(e)}")
                    continue
            
            resultado = {
                "success": True,
                "total": len(solicitudes_procesadas),
                "solicitudes": solicitudes_procesadas
            }
            
            print(f"✅ Historial obtenido exitosamente: {len(solicitudes_procesadas)} solicitudes")
            return resultado
            
        except Exception as e:
            print(f"❌ ERROR en get_historial_pagador: {str(e)}")
            raise
    
    def get_solicitudes_pendientes_comprobante(
        self,
        pagador_email: str,
        filtro_departamento: Optional[str] = None,
        filtro_tipo_pago: Optional[str] = None
    ) -> dict:
        """
        Obtener solicitudes pagadas que necesitan comprobantes de pago
        
        Args:
            pagador_email: Email del pagador actual
            filtro_departamento: Filtro opcional por departamento
            filtro_tipo_pago: Filtro opcional por tipo de pago
            
        Returns:
            Diccionario con solicitudes pendientes de comprobante
        """
        print(f"\n{'='*60}")
        print(f"📎 Obteniendo solicitudes pendientes de comprobante para: {pagador_email}")
        print(f"{'='*60}")
        
        try:
            # Construir query - solicitudes pagadas sin comprobantes o con comprobantes incompletos
            query = {
                "pagador_email": pagador_email,
                "estado": "pagada",
                "$or": [
                    {"comprobantes_pago": {"$exists": False}},
                    {"comprobantes_pago": {"$size": 0}},
                    {"comprobantes_pago": None}
                ]
            }
            
            # Aplicar filtros opcionales
            if filtro_departamento and filtro_departamento != "todos":
                query["departamento"] = filtro_departamento
                print(f"🏢 Filtro departamento: {filtro_departamento}")
            
            if filtro_tipo_pago and filtro_tipo_pago != "todos":
                query["tipo_pago"] = filtro_tipo_pago
                print(f"💳 Filtro tipo de pago: {filtro_tipo_pago}")
            
            print(f"🔎 Query: {query}")
            
            # Obtener solicitudes ordenadas por fecha de pago
            cursor = self.solicitudes_collection.find(query).sort("fecha_pago", -1)
            solicitudes = list(cursor)
            
            print(f"📊 Total de solicitudes pendientes de comprobante: {len(solicitudes)}")
            
            # Procesar solicitudes
            solicitudes_procesadas = []
            for sol in solicitudes:
                try:
                    # Convertir ObjectId a string
                    sol['id'] = str(sol['_id'])
                    
                    # Calcular días desde el pago y días restantes
                    if sol.get('fecha_pago'):
                        fecha_pago = sol['fecha_pago']
                        dias_desde_pago = (datetime.utcnow() - fecha_pago).days
                        sol['dias_desde_pago'] = dias_desde_pago
                        
                        # Calcular días restantes (3 días hábiles)
                        dias_restantes = 3 - dias_desde_pago
                        sol['dias_restantes_comprobante'] = max(0, dias_restantes)
                        
                        # Marcar si está vencido
                        sol['comprobante_vencido'] = dias_restantes < 0
                    
                    solicitudes_procesadas.append(sol)
                    
                except Exception as e:
                    print(f"⚠️ Error procesando solicitud {sol.get('_id')}: {str(e)}")
                    continue
            
            resultado = {
                "success": True,
                "total": len(solicitudes_procesadas),
                "solicitudes": solicitudes_procesadas
            }
            
            print(f"✅ Solicitudes pendientes obtenidas: {len(solicitudes_procesadas)}")
            return resultado
            
        except Exception as e:
            print(f"❌ ERROR en get_solicitudes_pendientes_comprobante: {str(e)}")
            raise
    
    def get_solicitudes_con_comprobantes(
        self,
        pagador_email: str,
        filtro_departamento: Optional[str] = None,
        filtro_tipo_pago: Optional[str] = None
    ) -> dict:
        """
        Obtener solicitudes pagadas que ya tienen comprobantes subidos
        
        Args:
            pagador_email: Email del pagador actual
            filtro_departamento: Filtro opcional por departamento
            filtro_tipo_pago: Filtro opcional por tipo de pago
            
        Returns:
            Diccionario con solicitudes que tienen comprobantes
        """
        print(f"\n{'='*60}")
        print(f"📄 Obteniendo solicitudes con comprobantes para: {pagador_email}")
        print(f"{'='*60}")
        
        try:
            # Construir query - solicitudes pagadas con comprobantes
            query = {
                "pagador_email": pagador_email,
                "estado": "pagada",
                "comprobantes_pago": {"$exists": True, "$ne": [], "$ne": None}
            }
            
            # Aplicar filtros opcionales
            if filtro_departamento and filtro_departamento != "todos":
                query["departamento"] = filtro_departamento
                print(f"🏢 Filtro departamento: {filtro_departamento}")
            
            if filtro_tipo_pago and filtro_tipo_pago != "todos":
                query["tipo_pago"] = filtro_tipo_pago
                print(f"💳 Filtro tipo de pago: {filtro_tipo_pago}")
            
            print(f"🔎 Query: {query}")
            
            # Obtener solicitudes ordenadas por fecha de subida de comprobante
            cursor = self.solicitudes_collection.find(query).sort("fecha_pago", -1)
            solicitudes = list(cursor)
            
            print(f"📊 Total de solicitudes con comprobantes: {len(solicitudes)}")
            
            # Procesar solicitudes
            solicitudes_procesadas = []
            for sol in solicitudes:
                try:
                    # Convertir ObjectId a string
                    sol['id'] = str(sol['_id'])
                    
                    # Contar comprobantes
                    num_comprobantes = len(sol.get('comprobantes_pago', []))
                    sol['num_comprobantes'] = num_comprobantes
                    
                    # Calcular días desde el pago
                    if sol.get('fecha_pago'):
                        dias_desde_pago = (datetime.utcnow() - sol['fecha_pago']).days
                        sol['dias_desde_pago'] = dias_desde_pago
                    
                    solicitudes_procesadas.append(sol)
                    
                except Exception as e:
                    print(f"⚠️ Error procesando solicitud {sol.get('_id')}: {str(e)}")
                    continue
            
            resultado = {
                "success": True,
                "total": len(solicitudes_procesadas),
                "solicitudes": solicitudes_procesadas
            }
            
            print(f"✅ Solicitudes con comprobantes obtenidas: {len(solicitudes_procesadas)}")
            return resultado
            
        except Exception as e:
            print(f"❌ ERROR en get_solicitudes_con_comprobantes: {str(e)}")
            raise


# Instancia global del controlador
pagador_controller = PagadorController()
