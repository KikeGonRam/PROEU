from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TipoMoneda(str, Enum):
    PESO_MX = "Peso Mexicano (MXN)"
    PESO_AR = "Peso Argentino (ARS)"
    PESO_CO = "Peso Colombiano (COP)"
    EURO = "Euro (EUR)"
    DOLAR = "Dólar Estadounidense (USD)"
    DOLAR_CA = "Dólar Canadiense (CAD)"

class TipoPago(str, Enum):
    PROVEEDORES = "Proveedores"
    POLIZA_SEGURO = "Póliza - Seguro"
    DONATIVOS = "Donativos"
    OPERATIVOS = "Operativos"
    FISCALES = "Fiscales y Legales"

class ConceptoPago(str, Enum):
    PAGOS_TERCEROS = "Pagos a Terceros"
    DONATIVOS = "Donativos"
    OTROS = "Otros"

class Departamento(str, Enum):
    RECTORÍA = "Rectoría"
    ACADEMICA = "Dirección Académica"
    ADMINISTRATIVA = "Dirección Administrativa"
    FINANZAS = "Finanzas"
    RECURSOS_HUMANOS = "Recursos Humanos"
    SISTEMAS = "Sistemas y TI"
    MANTENIMIENTO = "Mantenimiento"
    BIBLIOTECA = "Biblioteca"
    SERVICIOS_ESCOLARES = "Servicios Escolares"
    VINCULACION = "Vinculación"

class BancoDestino(str, Enum):
    BBVA = "BBVA México"
    BANAMEX = "Citibanamex"
    SANTANDER = "Santander México"
    BANORTE = "Banorte"
    HSBC = "HSBC México"
    SCOTIABANK = "Scotiabank"
    INBURSA = "Banco Inbursa"
    AZTECA = "Banco Azteca"
    BAJIO = "Banco del Bajío"
    AFIRME = "Banco Afirme"

class EstadoSolicitud(str, Enum):
    BORRADOR = "borrador"
    ENVIADA = "enviada"
    EN_REVISION = "en_revision"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"
    PAGADA = "pagada"
    CANCELADA = "cancelada"

class ArchivoAdjunto(BaseModel):
    nombre_archivo: str
    tipo_archivo: str
    tamaño: int
    ruta_archivo: str
    fecha_subida: datetime

class SolicitudEstandar(BaseModel):
    # Campos principales
    departamento: Departamento
    monto: float = Field(..., gt=0, description="Monto debe ser mayor a 0")
    tipo_moneda: TipoMoneda
    
    # Información bancaria
    banco_destino: BancoDestino
    cuenta_destino: str = Field(..., min_length=10, max_length=18)
    es_clabe: bool = Field(default=True, description="True si es CLABE, False si es cuenta tradicional")
    
    # Beneficiario principal
    nombre_beneficiario: str = Field(..., min_length=2, max_length=100)
    nombre_empresa: str = Field(..., min_length=2, max_length=150)
    
    # Beneficiario secundario (opcional)
    segundo_beneficiario: Optional[str] = Field(None, max_length=100)
    
    # Tipo y concepto de pago
    tipo_pago: TipoPago
    concepto_pago: ConceptoPago
    concepto_otros: Optional[str] = Field(None, description="Solo si concepto_pago es 'Otros'")
    
    # Fechas y descripción
    fecha_limite_pago: datetime
    descripcion_tipo_pago: str = Field(..., min_length=10, max_length=500)
    
    # Archivos adjuntos
    archivos_adjuntos: List[ArchivoAdjunto] = Field(default_factory=list)
    
    # Metadatos del sistema
    id: Optional[str] = None
    solicitante_email: Optional[str] = None
    estado: EstadoSolicitud = Field(default=EstadoSolicitud.BORRADOR)
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    
    # Comentarios del flujo de aprobación
    comentarios_solicitante: Optional[str] = None
    comentarios_aprobador: Optional[str] = None
    comentarios_pagador: Optional[str] = None
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SolicitudEstandarCreate(BaseModel):
    departamento: Departamento
    monto: float = Field(..., gt=0)
    tipo_moneda: TipoMoneda
    banco_destino: BancoDestino
    cuenta_destino: str = Field(..., min_length=10, max_length=18)
    es_clabe: bool = True
    nombre_beneficiario: str = Field(..., min_length=2, max_length=100)
    nombre_empresa: str = Field(..., min_length=2, max_length=150)
    segundo_beneficiario: Optional[str] = None
    tipo_pago: TipoPago
    concepto_pago: ConceptoPago
    concepto_otros: Optional[str] = None
    fecha_limite_pago: datetime
    descripcion_tipo_pago: str = Field(..., min_length=10, max_length=500)
    comentarios_solicitante: Optional[str] = None

class SolicitudEstandarUpdate(BaseModel):
    departamento: Optional[Departamento] = None
    monto: Optional[float] = Field(None, gt=0)
    tipo_moneda: Optional[TipoMoneda] = None
    banco_destino: Optional[BancoDestino] = None
    cuenta_destino: Optional[str] = Field(None, min_length=10, max_length=18)
    es_clabe: Optional[bool] = None
    nombre_beneficiario: Optional[str] = Field(None, min_length=2, max_length=100)
    nombre_empresa: Optional[str] = Field(None, min_length=2, max_length=150)
    segundo_beneficiario: Optional[str] = None
    tipo_pago: Optional[TipoPago] = None
    concepto_pago: Optional[ConceptoPago] = None
    concepto_otros: Optional[str] = None
    fecha_limite_pago: Optional[datetime] = None
    descripcion_tipo_pago: Optional[str] = Field(None, min_length=10, max_length=500)
    comentarios_solicitante: Optional[str] = None
    estado: Optional[EstadoSolicitud] = None

class SolicitudAprobacion(BaseModel):
    """Modelo para aprobar una solicitud"""
    solicitud_id: str = Field(..., description="ID de la solicitud a aprobar")
    comentarios_aprobador: Optional[str] = Field(
        None, 
        max_length=500,
        description="Comentarios opcionales del aprobador"
    )
    aprobador_email: Optional[str] = Field(
        None, 
        description="Email del aprobador (se obtiene automáticamente del token)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "solicitud_id": "507f1f77bcf86cd799439011",
                "comentarios_aprobador": "Solicitud aprobada. Proceder con el pago."
            }
        }

class SolicitudRechazo(BaseModel):
    """Modelo para rechazar una solicitud"""
    solicitud_id: str = Field(..., description="ID de la solicitud a rechazar")
    comentarios_aprobador: str = Field(
        ..., 
        min_length=10,
        max_length=500,
        description="Comentarios OBLIGATORIOS explicando el motivo del rechazo"
    )
    aprobador_email: Optional[str] = Field(
        None, 
        description="Email del aprobador (se obtiene automáticamente del token)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "solicitud_id": "507f1f77bcf86cd799439011",
                "comentarios_aprobador": "Rechazada por falta de documentación. Favor de adjuntar factura original."
            }
        }

class SolicitudPago(BaseModel):
    """Modelo para marcar una solicitud como pagada"""
    solicitud_id: str = Field(..., description="ID de la solicitud a marcar como pagada")
    fecha_pago: Optional[datetime] = Field(
        None, 
        description="Fecha del pago (se asigna automáticamente si no se proporciona)"
    )
    referencia_pago: Optional[str] = Field(
        None,
        max_length=100,
        description="Referencia o número de transacción del pago"
    )
    comentarios_pagador: Optional[str] = Field(
        None,
        max_length=500,
        description="Comentarios opcionales del pagador"
    )
    pagador_email: Optional[str] = Field(
        None, 
        description="Email del pagador (se obtiene automáticamente del token)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "solicitud_id": "507f1f77bcf86cd799439011",
                "referencia_pago": "TRX-20231215-001234",
                "comentarios_pagador": "Pago realizado exitosamente vía transferencia bancaria"
            }
        }

class SolicitudComprobantesPago(BaseModel):
    """Modelo para registrar comprobantes de pago subidos"""
    solicitud_id: str = Field(..., description="ID de la solicitud")
    # Los archivos se manejarán como UploadFile en el endpoint
    # Este modelo solo valida el solicitud_id
    
    class Config:
        json_schema_extra = {
            "example": {
                "solicitud_id": "507f1f77bcf86cd799439011"
            }
        }