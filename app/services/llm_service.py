# ByKP: Servicio de Inteligencia Artificial (LLM API)
# app/services/llm_service.py
# Célula 04 - Asistente Virtual SIS-UNETI

from app.config import settings
import httpx

async def responder_con_ia(mensaje_usuario: str, conversation_id: str):
    """
    Llama a la API de LLM configurada para obtener una respuesta.
    Si no hay API_KEY, devuelve un mensaje de error controlado.
    """
    if not settings.LLM_API_KEY:
        return {
            "respuesta": "Lo siento, mi cerebro de IA no está configurado (falta API Key). Por favor, contacta al administrador.",
            "confianza": 0.0,
            "fuente": "error_config",
            "requiere_escalado": True,
            "intencion": "nlu_error"
        }

    # ByKP: Ejemplo de integración con OpenAI-compatible API
    url = f"{settings.LLM_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": "Eres el Asistente Virtual de la UNETI (Universidad Nacional Experimental de las Telecomunicaciones e Informática). Tu objetivo es ser amable, profesional y ayudar a los estudiantes."},
            {"role": "user", "content": mensaje_usuario}
        ],
        "temperature": 0.7
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)
            data = response.json()
            
            if response.status_code == 200:
                respuesta_texto = data["choices"][0]["message"]["content"]
                return {
                    "respuesta": respuesta_texto,
                    "confianza": 0.85, # Estimación fija por ahora
                    "fuente": f"llm_{settings.LLM_MODEL}",
                    "requiere_escalado": False,
                    "intencion": "ia_generative"
                }
            else:
                return {
                    "respuesta": "Tuve un problema al procesar tu duda con mi motor de IA.",
                    "confianza": 0.0,
                    "fuente": "api_error",
                    "requiere_escalado": True,
                    "intencion": "error"
                }

    except Exception as e:
        print(f"❌ Error en LLM Service: {e}")
        return {
            "respuesta": "Mi motor de IA está fuera de línea en este momento.",
            "confianza": 0.0,
            "fuente": "exception",
            "requiere_escalado": True,
            "intencion": "error"
        }
