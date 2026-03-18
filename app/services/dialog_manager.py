from app.core.redis_client import redis_client
import json
from uuid import UUID
from typing import Optional, Dict, Any
from datetime import datetime

CONTEXT_TTL = 1800  # 30 minutos

async def obtener_contexto(sesion_id: UUID) -> Dict[str, Any]:
    key = f"sesion:{sesion_id}"
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return {}

async def guardar_contexto(sesion_id: UUID, contexto: Dict[str, Any]):
    key = f"sesion:{sesion_id}"
    await redis_client.setex(key, CONTEXT_TTL, json.dumps(contexto))

async def actualizar_contexto(sesion_id: UUID, **kwargs):
    contexto = await obtener_contexto(sesion_id)
    contexto.update(kwargs)
    await guardar_contexto(sesion_id, contexto)

async def agregar_mensaje(sesion_id: UUID, rol: str, contenido: str, intencion: str = None, capa: int = None, confianza: float = None):
    contexto = await obtener_contexto(sesion_id)
    historial = contexto.get("historial", [])
    historial.append({
        "rol": rol,
        "contenido": contenido,
        "intencion": intencion,
        "capa": capa,
        "confianza": confianza,
        "timestamp": str(datetime.utcnow())
    })
    # Limitar historial a últimos 20 mensajes
    if len(historial) > 20:
        historial = historial[-20:]
    contexto["historial"] = historial
    await guardar_contexto(sesion_id, contexto)

# Para uso interno en endpoints