import httpx
from app.core.config import settings
from app.services.nlu_utils import detectar_intencion, extraer_entidades
from app.utils.personalidad import SYSTEM_PROMPT
import logging

logger = logging.getLogger(__name__)

async def generar_respuesta_llm(
    mensaje: str, 
    contexto: dict, 
    db_session  # para posible consulta a base conocimiento
) -> tuple[str, float, str]:
    """
    Invoca modelo Ollama, integrando información del contexto y datos del core.
    Retorna (respuesta, confianza, intención)
    """
    intencion, conf_int = detectar_intencion(mensaje)
    entidades = extraer_entidades(mensaje)

    # Aquí se podría consultar al core para obtener datos en tiempo real
    # y pasarlos como contexto adicional al LLM.
    # Por simplicidad, construimos un prompt con la información disponible.

    # Si la intención es consultar notas y tenemos sesión con estudiante_id,
    # podríamos llamar a sis_client para obtener notas reales.
    # (se implementará más adelante)

    from datetime import datetime
    ahora = datetime.now()
    fecha_formateada = ahora.strftime("%d de %B de %Y, %I:%M %p")
    
    system_content = f"{SYSTEM_PROMPT}\nFecha actual: {fecha_formateada}"

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": "Hola"},
        {"role": "assistant", "content": "¡Hola! Soy Uneti-Pocket, tu asistente de la UNETI. ¿En qué puedo ayudarte hoy? ✅"},
        {"role": "user", "content": "gracias"},
        {"role": "assistant", "content": "¡De nada! Siempre a la orden. Si tienes más dudas sobre la universidad, aquí estaré. 😊"},
    ]
    
    # Agregar historial real (últimos 3 para no saturar)
    for msg in contexto.get('historial', [])[-3:]:
        role = "user" if msg["rol"] == "USUARIO" else "assistant"
        messages.append({"role": role, "content": msg["contenido"]})
        
    # Agregar mensaje actual
    messages.append({"role": "user", "content": mensaje})

    # Llamada a Ollama via chat API (mejor manejo de templates)
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{settings.OLLAMA_URL}/api/chat",
                json={
                    "model": settings.LLM_MODEL,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 200
                    }
                },
                timeout=300.0
            )
            
            if resp.status_code == 200:
                data = resp.json()
                respuesta = data.get("message", {}).get("content", "").strip()
                confianza = 0.8 if respuesta else 0.2
            else:
                logger.error(f"Error en Ollama Status: {resp.status_code} - {resp.text}")
                respuesta = ""
                confianza = 0.0
                
        except Exception as e:
            logger.error(f"Error en conexión con Ollama: {e}")
            respuesta = ""
            confianza = 0.0

    # Si no hubo respuesta de Ollama, delegamos a Capa 3
    return respuesta, confianza, intencion

def _formatear_historial(historial):
    if not historial:
        return "No hay mensajes previos."
    lines = []
    for msg in historial[-3:]:  # últimos 3
        rol = "Estudiante" if msg["rol"] == "USUARIO" else "Asistente"
        lines.append(f"{rol}: {msg['contenido']}")
    return "\n".join(lines)