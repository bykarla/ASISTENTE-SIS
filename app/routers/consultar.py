# ByKP: Endpoint Principal de Conversación
# app/routers/consultar.py
# Célula 04 - Asistente Virtual SIS-UNETI

from fastapi import APIRouter, Depends
import time
import uuid
from app.schemas import ConsultaRequest, ConsultaResponse
from app.services.keyword_matcher import buscar_respuesta_faq
from app.dependencies import get_db
from app.services.llm_service import responder_con_ia

# Creamos el enrutador para agrupar las rutas de conversación
router = APIRouter(prefix="/api/v1", tags=["Conversación"])

@router.post("/consultar", response_model=ConsultaResponse)
async def consultar_asistente(request: ConsultaRequest, db = Depends(get_db)):
    """
    Recibe un mensaje del estudiante, lo procesa por capas y devuelve una respuesta.
    """
    start_time = time.time()
    
    # 1. Asignar o reutilizar el ID de la conversación actual
    conv_id = request.contexto_conversacion_id or str(uuid.uuid4())
    
    # 2. CAPA 1: Búsqueda Rápida en Base de Datos (Keyword Matcher)
    faq_match = buscar_respuesta_faq(db, request.mensaje)
    
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
            intencion_detectada="faq_match"
        )
        
    # 3. CAPA 2: IA Generativa (LLM API) - Fallback
    # Si no hay match en FAQ, le pedimos a la IA que responda
    res_ia = await responder_con_ia(request.mensaje, conv_id)
    
    tiempo_ms = int((time.time() - start_time) * 1000)
    return ConsultaResponse(
        respuesta=res_ia["respuesta"],
        conversation_id=conv_id,
        capa_utilizada=2,
        confianza=res_ia["confianza"],
        fuente=res_ia["fuente"],
        requiere_escalado=res_ia["requiere_escalado"],
        tiempo_procesamiento_ms=tiempo_ms,
        intencion_detectada=res_ia["intencion"]
    )