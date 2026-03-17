# ByKP: DTOs (Data Transfer Objects) para el Asistente Virtual SIS-UNETI 2026
# Cumplimiento estricto de tipado y validación de seguridad (Célula 04)

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# ============================================================================
# 1. MODELOS BASE (Entidades de Base de Datos)
# ============================================================================

# --- Conocimiento (Capa 1: FAQs) ---
class ConocimientoBase(BaseModel):
    categoria: str = Field(..., max_length=50, description="Categoría principal (ej. Inscripciones)")
    subcategoria: Optional[str] = Field(None, max_length=50, description="Subcategoría opcional")
    pregunta_patron: str = Field(..., description="Pregunta o patrón representativo")
    # ByKP: Se usa 'alias' para mapear 'palabras_clave' de la BD a 'tags' en el JSON del Frontend
    tags: List[str] = Field(..., alias="palabras_clave", description="Palabras clave para búsqueda rápida (tags)")
    respuesta: str = Field(..., description="Respuesta predefinida")
    acceso_publico: bool = Field(True, description="Visible sin autenticación")
    prioridad: int = Field(0, ge=0, description="Prioridad para ordenar resultados")
    activo: bool = Field(True, description="Si está activo para uso")
    
    # ByKP: Mejora - Se añade 'from_attributes' para permitir la conversión automática de objetos ORM (PostgreSQL) a JSON
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

class ConocimientoCreate(ConocimientoBase):
    pass

class ConocimientoUpdate(BaseModel):
    categoria: Optional[str] = Field(None, max_length=50)
    subcategoria: Optional[str] = None
    pregunta_patron: Optional[str] = None
    tags: Optional[List[str]] = None
    respuesta: Optional[str] = None
    acceso_publico: Optional[bool] = None
    prioridad: Optional[int] = Field(None, ge=0)
    activo: Optional[bool] = None

class Conocimiento(ConocimientoBase):
    id: UUID
    veces_utilizada: int = Field(0, description="Contador de usos")
    version: int = Field(1)
    creado_por: Optional[str] = None
    aprobado_por: Optional[str] = None
    # ByKP: Mejora - Se cambia 'str' por 'datetime' nativo para garantizar compatibilidad con PostgreSQL y auditoría
    created_at: datetime
    updated_at: datetime


# --- Intenciones (NLU - Capa 2) ---
class IntencionBase(BaseModel):
    codigo: str = Field(..., max_length=50, description="Código único de la intención")
    nombre_display: str = Field(..., max_length=100, description="Nombre para mostrar")
    descripcion: Optional[str] = None
    entidades_esperadas: List[str] = Field(default_factory=list, description="Lista de entidades que se esperan")
    api_core_asociada: Optional[str] = Field(None, max_length=150, description="Endpoint del core asociado")
    accion_tipo: str = Field("respuesta", pattern="^(respuesta|escalado|redireccion)$")
    requiere_auth: bool = False
    activo: bool = True

class Intencion(IntencionBase):
    id: UUID
    created_at: datetime

class EjemploIntencion(BaseModel):
    id: Optional[UUID] = None
    intencion_id: UUID
    texto_ejemplo: str
    idioma: str = "es"


# --- Sesiones de Conversación ---
class SesionBase(BaseModel):
    estudiante_id: Optional[UUID] = None
    estudiante_cedula: Optional[str] = Field(None, max_length=15)
    canal: str = Field("WEB", pattern="^(WEB|API)$")
    ip_origen: Optional[str] = None
    agente_usuario: Optional[str] = None

class SesionCreate(SesionBase):
    pass

class SesionUpdate(BaseModel):
    # ByKP: Mejora - Uso de datetime para facilitar el cálculo de TTL (Time To Live) de 30 min en Redis
    fecha_fin: Optional[datetime] = None
    estado: Optional[str] = Field(None, pattern="^(ACTIVA|CERRADA|ESCALADA|ABANDONADA)$")
    capa_maxima_usada: Optional[int] = Field(None, ge=1, le=3)
    total_mensajes: Optional[int] = None
    satisfaccion_usuario: Optional[int] = Field(None, ge=1, le=5)
    retroalimentacion_texto: Optional[str] = None
    retroalimentacion_fecha: Optional[datetime] = None

class Sesion(SesionBase):
    id: UUID
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    estado: str
    capa_maxima_usada: Optional[int] = None
    total_mensajes: int
    satisfaccion_usuario: Optional[int] = None
    retroalimentacion_texto: Optional[str] = None
    retroalimentacion_fecha: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# --- Mensajes ---
class MensajeBase(BaseModel):
    sesion_id: UUID
    rol: str = Field(..., pattern="^(USUARIO|ASISTENTE|HUMANO|SISTEMA)$")
    tipo_entrada: str = Field("texto", pattern="^(texto|comando)$")
    contenido: str
    intencion_detectada: Optional[str] = None
    confianza_intencion: Optional[float] = Field(None, ge=0, le=1)
    entidades_extraidas: Optional[dict] = None
    capa_respuesta: Optional[int] = Field(None, ge=1, le=3)
    tiempo_respuesta_ms: Optional[int] = Field(None, ge=0)
    fuente_respuesta: Optional[str] = Field(None, max_length=30)
    tokens_consumidos: Optional[int] = Field(None, ge=0)

class MensajeCreate(MensajeBase):
    pass

class Mensaje(MensajeBase):
    id: UUID
    created_at: datetime


# --- Escalado a Humano (Capa 3) ---
class EscaladoBase(BaseModel):
    sesion_id: UUID
    estudiante_id: UUID
    departamento_destino: str = Field(..., pattern="^(SECRETARIA|COORDINACION|CONTROL_ESTUDIOS)$")
    # ByKP: Se estandariza 'motivo_escalado' para que coincida exactamente con el contrato de Nest.js y el .sql
    motivo_escalado: str = Field(..., pattern="^(BAJA_CONFIANZA|SOLICITUD_USUARIO|TEMA_SENSIBLE|SIN_RESOLUCION|OTRO)$")
    resumen_conversacion: str
    contexto_json: Optional[dict] = None
    prioridad: str = Field("NORMAL", pattern="^(BAJA|NORMAL|ALTA|URGENTE)$")
    estado: str = Field("PENDIENTE", pattern="^(PENDIENTE|EN_ATENCION|RESUELTO|CERRADO)$")
    operador_asignado: Optional[str] = None
    fecha_asignacion: Optional[datetime] = None
    fecha_resolucion: Optional[datetime] = None
    notas_operador: Optional[str] = None

class EscaladoCreate(EscaladoBase):
    pass

class Escalado(EscaladoBase):
    id: UUID
    created_at: datetime


# ============================================================================
# 2. MODELOS REQUEST/RESPONSE (Contratos de la API)
# ============================================================================

# --- Endpoint: POST /api/v1/consultar ---
class ConsultaRequest(BaseModel):
    mensaje: str = Field(..., max_length=2000, description="Mensaje del estudiante")
    contexto_conversacion_id: Optional[str] = Field(None, description="UUID de la sesión activa (si existe)")
    # ByKP: Mejora - Inclusión de metadata para trazar dispositivo/idioma sin romper el esquema principal
    metadata: Optional[dict] = Field(None, description="Información adicional (ej. idioma preferido)")

class ConsultaResponse(BaseModel):
    respuesta: str = Field(..., description="Respuesta generada")
    conversation_id: str = Field(..., description="UUID de la sesión (nuevo o existente)")
    capa_utilizada: int = Field(..., ge=1, le=3, description="Capa que respondió (1,2,3)")
    confianza: Optional[float] = Field(None, ge=0, le=1, description="Confianza de la respuesta (para Capa 2)")
    fuente: Optional[str] = Field(None, description="Fuente específica: 'faq', 'llm_local', 'api_core', etc.")
    requiere_escalado: bool = Field(False, description="Si el sistema sugiere escalar a humano")
    # ByKP: Mejora - Se añaden tags sugeridos para mejorar la experiencia UX de búsqueda rápida en el Frontend
    tags_sugeridos: Optional[List[str]] = Field(None, description="Tags relacionados para búsqueda rápida")
    # ByKP: Mejora - Inclusión de tiempos y diagnóstico para auditoría técnica en tiempo real
    tiempo_procesamiento_ms: Optional[int] = None
    intencion_detectada: Optional[str] = None


# --- Endpoint: POST /api/v1/escalar ---
class EscalarRequest(BaseModel):
    conversation_id: str = Field(..., description="UUID de la sesión activa")
    # ByKP: Mejora - Unificación de nombre de campo a 'motivo_escalado' para consistencia total con BD y JSON
    motivo_escalado: str = Field(..., max_length=500, description="Razón del escalado")
    resumen_conversacion: str = Field(..., description="Resumen breve de la duda para el operador")
    user_message: str = Field(..., description="Último mensaje del usuario que provocó el escalado")
    departamento_destino: Optional[str] = Field("SECRETARIA", description="Departamento al que se dirige")

class EscalarResponse(BaseModel):
    ticket_id: Optional[str] = Field(None, description="UUID del ticket generado (en BD local)")
    nestjs_ticket_id: Optional[str] = Field(None, description="ID del ticket en Nest.js (si aplica)")
    status: str = Field(..., pattern="^(creado|error)$")
    mensaje: str
    fecha_creacion: Optional[datetime] = None