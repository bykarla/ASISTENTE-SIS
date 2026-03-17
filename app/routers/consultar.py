# ByKP: Endpoint Principal de Conversación
# app/routers/consultar.py
# Célula 04 - Asistente Virtual SIS-UNETI

from fastapi import APIRouter
import time
import uuid
from app.schemas import ConsultaRequest, ConsultaResponse
from app.services.keyword_matcher import buscar_respuesta_faq

# Creamos el enrutador para agrupar las rutas de conversación
router = APIRouter(prefix="/api/v1", tags=["Conversación"])

@router.post("/consultar", response_model=ConsultaResponse)
async def consultar_asistente(request: ConsultaRequest):
    """
    Recibe un mensaje del estudiante, lo procesa y devuelve una respuesta estructurada.
    """
    start_time = time.time()
    
    # 1. Asignar o reutilizar el ID de la conversación actual
    conv_id = request.contexto_conversacion_id or str(uuid.uuid4())
    
    # 2. CAPA 1: Búsqueda Rápida en Base de Datos (Keyword Matcher)
    faq_match = buscar_respuesta_faq(request.mensaje)
    
    if faq_match:
        tiempo_ms = int((time.time() - start_time) * 1000)
        
        # Devolvemos el Contrato JSON exacto que definimos en los Schemas
        return ConsultaResponse(
            respuesta=faq_match["respuesta"],
            conversation_id=conv_id,
            capa_utilizada=1,
            confianza=faq_match["confianza"],
            fuente="faq_postgresql",
            requiere_escalado=False,
            tags_sugeridos=faq_match["tags"][:3], # Le sugerimos 3 tags al frontend
            tiempo_procesamiento_ms=tiempo_ms,
            intencion_detectada="faq_match"
        )
        
    # 3. FALLBACK (Si no encuentra respuesta en Capa 1)
    # TODO: Aquí es donde en la siguiente fase conectaremos a la Capa 2 (LLM / IA Generativa)
    tiempo_ms = int((time.time() - start_time) * 1000)
    return ConsultaResponse(
        respuesta="Aún estoy aprendiendo y no tengo una respuesta exacta para eso. ¿Podrías intentar usar otras palabras clave? O si prefieres, puedes contactar a Control de Estudios.",
        conversation_id=conv_id,
        capa_utilizada=1, # 1 indica que se utilizó la capa de búsqueda rápida
        confianza=0.0,
        fuente="fallback",
        requiere_escalado=True, # Sugerimos escalar a humano
        tiempo_procesamiento_ms=tiempo_ms
    )