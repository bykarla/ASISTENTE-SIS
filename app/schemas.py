# ByKP: DTOs (Data Transfer Objects) para el Asistente Virtual SIS-UNETI 2026
# Ruta: app/schemas.py
# Cumplimiento estricto de tipado y validación de seguridad (Célula 04)
# Actualizado para sincronizar con Issue #2 (Iván Vásquez - QA)

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# ============================================================================
# 1. MODELOS BASE (Entidades de Base de Datos)
# ============================================================================

class ConocimientoBase(BaseModel):
    """
    Molde estricto para las FAQs ingeridas desde la Base de Conocimiento.
    Actualizado según los estándares de QA para el Issue #2.
    """
    categoria: str = Field(..., max_length=100)
    subcategoria: str = Field(default="Pendiente de Definir", max_length=100)
    pregunta_patron: str = Field(...)
    tags: List[str] = Field(..., alias="palabras_clave")
    respuesta: str = Field(...)
    acceso_publico: bool = Field(True)
    # ByKP: Ajustado a la nueva escala de criticidad 1-10 dictada por QA
    prioridad: int = Field(5, ge=1, le=10)
    activo: bool = Field(True)
    fuente: Optional[str] = Field(None, description="Origen de la FAQ (ej. Ticket Orgánico)")
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class ConocimientoCreate(ConocimientoBase):
    pass

# ============================================================================
# 2. MODELOS DE CONVERSACIÓN (Request / Response)
# ============================================================================

class ConsultaRequest(BaseModel):
    mensaje: str = Field(..., min_length=2, max_length=500)
    contexto_conversacion_id: Optional[str] = None
    metadata: Optional[dict] = None

class ConsultaResponse(BaseModel):
    respuesta: str
    conversation_id: str
    capa_utilizada: int = Field(..., ge=1, le=3)
    confianza: float = Field(..., ge=0.0, le=1.0)
    fuente: str
    requiere_escalado: bool = False
    tags_sugeridos: Optional[List[str]] = None
    tiempo_procesamiento_ms: Optional[int] = None
    intencion_detectada: Optional[str] = None
    # ByKP: Bandera para la Deuda Técnica (Issue #2). Avisa si falta procesar con IA.
    requiere_generacion_ia: bool = Field(False)

# ============================================================================
# 3. MODELOS DE ESCALADO (Capa 3)
# ============================================================================

class EscalarRequest(BaseModel):
    conversation_id: str = Field(...)
    motivo_escalado: str = Field(..., max_length=500)
    resumen_conversacion: str = Field(...)
    user_message: str = Field(...)
    departamento_destino: Optional[str] = Field("SECRETARIA")

class EscalarResponse(BaseModel):
    ticket_id: Optional[str] = None
    nestjs_ticket_id: Optional[str] = None
    status: str = Field(...)
    mensaje: str
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)

# ============================================================================
# 4. MODELOS ACADÉMICOS (Fórmula Soberana)
# ============================================================================

class ResultadoSoberano(BaseModel):
    """
    Esquema para la respuesta de evaluación con doble escala.
    Cumple con el REQ-AC-02 para la integridad de actas.
    """
    nota_moodle: float = Field(..., ge=0, le=100)
    nota_uneti_20: float = Field(..., ge=1, le=20)
    nota_letras: str
    estado: str
    puede_cerrar_acta: bool
    descripcion: str