# ByKP: Servicio de Generación de Texto con IA (Capa 2)
# Ruta: app/services/llm_service.py
# Célula 04 - Asistente Virtual SIS-UNETI 2026

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "tinyllama")

async def reescribir_respuesta_ia(contexto_crudo: str, pregunta_estudiante: str) -> str:
    """
    Toma el texto crudo de la base de datos (con la incidencia) 
    y usa el LLM local para redactar una respuesta institucional amable.
    """
    # Limpiamos la etiqueta de QA para que no confunda a la IA
    contexto_limpio = contexto_crudo.replace("[PENDIENTE GENERAR CON IA]: ", "")
    
    # Probando Prompt estricto para evitar que TinyLlama repita las instrucciones
    prompt = (
        f"Pregunta del estudiante: {pregunta_estudiante}\n"
        f"Información para responder: {contexto_limpio}\n\n"
        "Instrucción: Escribe una respuesta amable, directa y corta para el estudiante usando la información dada. "
        "NO describas tu personalidad, NO repitas estas instrucciones, solo responde al estudiante.\n\n"
        "Respuesta:"
    )

    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False # Queremos la respuesta completa de una vez
    }

    try:
        # Petición asíncrona a Ollama
        async with httpx.AsyncClient() as client:
            respuesta_api = await client.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=120.0)
            respuesta_api.raise_for_status()
            datos = respuesta_api.json()
            return datos.get("response", "").strip()
            
    except Exception as e:
        print(f"❌ Error de conexión con Ollama ({LLM_MODEL}): {e}")
        # Fallback seguro en caso de que el motor de IA esté apagado
        return "Disculpa, en este momento mi sistema de razonamiento avanzado está en mantenimiento. Por favor, intenta de nuevo más tarde o contacta a soporte técnico."