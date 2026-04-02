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

    # ByKP: Construcción de la URL (Aseguramos que no haya dobles slashes y sea la ruta correcta)
    base_url = settings.LLM_BASE_URL.rstrip("/")
    url = f"{base_url}/chat/completions"
    
    print(f"📡 Llamando a LLM: {url} | Modelo: {settings.LLM_MODEL}")
    
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
            # ByKP: Aumentamos el timeout a 60s ya que los LLMs pueden tardar en generar respuestas largas
            response = await client.post(url, json=payload, headers=headers, timeout=60.0)
            data = response.json()
            
            if response.status_code == 200:
                respuesta_texto = data["choices"][0]["message"]["content"]
                return {
                    "respuesta": respuesta_texto,
                    "confianza": 0.85,
                    "fuente": f"llm_{settings.LLM_MODEL}",
                    "requiere_escalado": False,
                    "intencion": "ia_generative"
                }
            else:
                print(f"⚠️ OpenAI/DeepSeek API Error ({response.status_code}): {data}")
                # --- MODO SIMULACIÓN PARA DESARROLLO ---
                return {
                    "respuesta": f"[Modo Simulación] Tu motor de IA reportó un error {response.status_code}. Verifica tu API Key y saldo.",
                    "confianza": 0.5,
                    "fuente": "llm_mock_fallback",
                    "requiere_escalado": True,
                    "intencion": "api_error_fallback"
                }

    except Exception as e:
        # ByKP: Usamos repr(e) para obtener el nombre técnico del error (ej: ConnectTimeout)
        print(f"❌ Error crítico en LLM Service: {repr(e)}")
        return {
            "respuesta": "Mi motor de IA ha tardado demasiado o hay un problema de conexión.",
            "confianza": 0.0,
            "fuente": "exception",
            "requiere_escalado": True,
            "intencion": "error"
        }
