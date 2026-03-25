# ByKP: Endpoint Principal de Conversación
# Célula 04 - Asistente Virtual SIS-UNETI

from fastapi import APIRouter
import time
import uuid
from app.schemas import ConsultaRequest, ConsultaResponse
from app.services.keyword_matcher import buscar_respuesta_faq

router = APIRouter(prefix="/api/v1", tags=["Conversación"])

@router.post("/consultar", response_model=ConsultaResponse)
async def consultar_asistente(request: ConsultaRequest):
    """
    Recibe un mensaje del estudiante, lo procesa y devuelve una respuesta estructurada.
    """
    start_time = time.time()
    conv_id = request.contexto_conversacion_id or str(uuid.uuid4())
    
    # CAPA 1: Búsqueda Rápida en PostgreSQL con NLP
    faq_match = buscar_respuesta_faq(request.mensaje)
    
    if faq_match:
        tiempo_ms = int((time.time() - start_time) * 1000)
        
        return ConsultaResponse(
            respuesta=faq_match["respuesta"],
            conversation_id=conv_id,
            capa_utilizada=1,
            confianza=faq_match["confianza"],
            fuente="faq_postgresql",
            requiere_escalado=False,
            tags_sugeridos=faq_match["tags"][:3],
            tiempo_procesamiento_ms=tiempo_ms,
            intencion_detectada="faq_match",
            requiere_generacion_ia=faq_match["requiere_generacion_ia"] # Integración Issue #2
        )
        
    # FALLBACK
    tiempo_ms = int((time.time() - start_time) * 1000)
    return ConsultaResponse(
        respuesta="Aún estoy aprendiendo y no tengo una respuesta exacta para eso. ¿Podrías intentar usar otras palabras clave? O si prefieres, puedes contactar a Control de Estudios.",
        conversation_id=conv_id,
        capa_utilizada=1,
        confianza=0.0,
        fuente="fallback",
        requiere_escalado=True,
        tiempo_procesamiento_ms=tiempo_ms,
        requiere_generacion_ia=False
    )