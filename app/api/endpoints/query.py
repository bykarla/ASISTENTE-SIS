from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.schemas.request_response import QueryRequest, QueryResponse
from app.core.database import SessionLocal
from app.services import capa1_faq, capa2_nlp, capa3_escalado, dialog_manager, whisper_service
from app.models.orm import AsistenteSesion, AsistenteMensaje
from uuid import UUID, uuid4
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/query", response_model=QueryResponse)
async def consulta(
    request: Request,
    mensaje: str = Form(None),
    contexto_conversacion_id: str = Form(None),
    tipo_entrada: str = Form("texto"),
    audio: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """
    Endpoint principal para enviar consultas (texto o voz) al asistente.
    Si tipo_entrada es 'voz', se debe enviar el archivo de audio en el campo 'audio'.
    """
    sesion_id = None
    if contexto_conversacion_id:
        try:
            sesion_id = UUID(contexto_conversacion_id)
        except ValueError:
            sesion_id = None
    if not sesion_id:
        # Nueva sesión
        sesion_id = uuid4()
        # Crear registro en BD
        sesion_db = AsistenteSesion(id=sesion_id, estudiante_id=None)
        db.add(sesion_db)
        db.commit()

    # Obtener o crear contexto en Redis
    contexto = await dialog_manager.obtener_contexto(sesion_id)
    if not contexto:
        contexto = {"sesion_id": str(sesion_id), "historial": []}
        await dialog_manager.guardar_contexto(sesion_id, contexto)

    # Procesar entrada: si es voz, transcribir
    texto_consulta = mensaje
    if tipo_entrada == "voz" and audio:
        contenido_audio = await audio.read()
        texto_consulta = await whisper_service.transcribir_audio(contenido_audio)
        if not texto_consulta:
            texto_consulta = "[No se pudo transcribir el audio]"
        logger.info(f"Transcripción: {texto_consulta}")

    if not texto_consulta:
        raise HTTPException(status_code=400, detail="Mensaje vacío o no transcrito")

    # Guardar mensaje del usuario en contexto
    await dialog_manager.agregar_mensaje(sesion_id, "USUARIO", texto_consulta)

    # --- CAPA 1: FAQ por palabras clave ---
    respuesta_capa1, confianza_capa1, fuente_capa1 = capa1_faq.buscar_faq(texto_consulta, db)
    if respuesta_capa1 and confianza_capa1 >= 0.5:
        # Respuesta con Capa 1
        await dialog_manager.agregar_mensaje(sesion_id, "ASISTENTE", respuesta_capa1, capa=1, confianza=confianza_capa1)
        # Actualizar sesión en BD (opcional)
        return QueryResponse(
            respuesta=respuesta_capa1,
            capa_utilizada=1,
            confianza=confianza_capa1,
            fuente=fuente_capa1,
            requiere_escalado=False
        )

    # --- CAPA 2: NLP con LLM ---
    respuesta_capa2, confianza_capa2, intencion = await capa2_nlp.generar_respuesta_llm(
        texto_consulta, contexto, db
    )
    # Verificar si la respuesta es satisfactoria (confianza > umbral)
    if respuesta_capa2 and confianza_capa2 >= 0.6:
        await dialog_manager.agregar_mensaje(sesion_id, "ASISTENTE", respuesta_capa2, intencion, capa=2, confianza=confianza_capa2)
        return QueryResponse(
            respuesta=respuesta_capa2,
            capa_utilizada=2,
            confianza=confianza_capa2,
            requiere_escalado=False
        )

    # --- CAPA 3: Escalado a humano ---
    motivo = "No se pudo resolver con IA"
    datos_escalado = await capa3_escalado.escalar_a_humano(sesion_id, motivo, contexto)
    respuesta_escalado = (f"Lo siento, no pude resolver tu consulta automáticamente. "
                          f"Te estoy conectando con un agente de Secretaría. "
                          f"Ticket #{datos_escalado['ticket_id']}. Tiempo estimado: {datos_escalado['tiempo_estimado']}.")
    await dialog_manager.agregar_mensaje(sesion_id, "ASISTENTE", respuesta_escalado, capa=3, confianza=0.0)
    # Marcar sesión como ESCALADA en BD
    db.query(AsistenteSesion).filter(AsistenteSesion.id == sesion_id).update({"estado": "ESCALADA"})
    db.commit()

    return QueryResponse(
        respuesta=respuesta_escalado,
        capa_utilizada=3,
        confianza=0.0,
        requiere_escalado=True,
        datos_escalado=datos_escalado
    )