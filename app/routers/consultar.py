# ByKP: Endpoint Principal de Conversación
# Ruta: app/routers/consultar.py
# Célula 04 - Asistente Virtual SIS-UNETI

from fastapi import APIRouter
import time
import uuid
from app.schemas import ConsultaRequest, ConsultaResponse
from app.services.keyword_matcher import buscar_respuesta_faq
# ByKP: Importamos el servicio de Inteligencia Artificial (Ollama)
from app.services.llm_service import reescribir_respuesta_ia

router = APIRouter(prefix="/api/v1", tags=["Conversación"])

@router.post("/consultar", response_model=ConsultaResponse)
async def consultar_asistente(request: ConsultaRequest):
    """
    Recibe un mensaje del estudiante. Si la respuesta está pendiente de IA,
    invoca al modelo local (Ollama) para redactarla en tiempo real.
    """
    start_time = time.time()
    conv_id = request.contexto_conversacion_id or str(uuid.uuid4())
    
    # CAPA 1: Búsqueda Rápida en BD (Determinista)
    faq_match = buscar_respuesta_faq(request.mensaje)
    
    if faq_match:
        respuesta_final = faq_match["respuesta"]
        capa_usada = 1
        
        # CAPA 2: Inteligencia Artificial Generativa (Issue #2)
        if faq_match.get("requiere_generacion_ia"):
            # Llamamos a Ollama para que arregle el texto crudo
            respuesta_final = await reescribir_respuesta_ia(
                contexto_crudo=respuesta_final, 
                pregunta_estudiante=request.mensaje
            )
            capa_usada = 2 # Indicamos que se usó la Capa de IA
            
        tiempo_ms = int((time.time() - start_time) * 1000)
        
        return ConsultaResponse(
            respuesta=respuesta_final,
            conversation_id=conv_id,
            capa_utilizada=capa_usada, # Será 1 si es BD directa, o 2 si usó Ollama
            confianza=faq_match["confianza"],
            fuente="faq_postgresql" if capa_usada == 1 else "llm_ollama",
            requiere_escalado=False,
            tags_sugeridos=faq_match.get("tags", [])[:3],
            tiempo_procesamiento_ms=tiempo_ms,
            intencion_detectada="faq_match",
            requiere_generacion_ia=False # Ya fue resuelto por la IA
        )
        
    # FALLBACK (Si no encuentra nada, prepara para Capa 3 / Escalado)
    tiempo_ms = int((time.time() - start_time) * 1000)
    return ConsultaResponse(
        respuesta="Aún estoy aprendiendo. ¿Podrías intentar usar otras palabras clave? O si prefieres, puedes contactar a Control de Estudios.",
        conversation_id=conv_id,
        capa_utilizada=1,
        confianza=0.0,
        fuente="fallback",
        requiere_escalado=True,
        tiempo_procesamiento_ms=tiempo_ms,
        requiere_generacion_ia=False
    )