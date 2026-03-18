from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class QueryRequest(BaseModel):
    mensaje: Optional[str] = None
    contexto_conversacion_id: Optional[UUID] = None
    tipo_entrada: str = "texto"  # "texto" o "voz"

class QueryResponse(BaseModel):
    respuesta: str
    capa_utilizada: int
    confianza: float
    fuente: Optional[str] = None
    requiere_escalado: bool = False
    datos_escalado: Optional[Dict[str, Any]] = None

class AudioQueryRequest(BaseModel):
    # Se usará multipart/form-data, no es necesario modelo aquí
    pass

class FAQCreate(BaseModel):
    categoria: str
    pregunta_patron: str
    palabras_clave: List[str]
    respuesta: str

class FAQOut(FAQCreate):
    id: UUID
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True