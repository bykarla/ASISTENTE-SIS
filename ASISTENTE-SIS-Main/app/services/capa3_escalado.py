from typing import Dict, Any
from uuid import uuid4

async def escalar_a_humano(sesion_id, motivo: str, contexto: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea un ticket de escalado y retorna información para la respuesta.
    En un sistema real, se almacenaría en BD y se notificaría al panel de operadores.
    """
    ticket_id = uuid4()
    # Aquí se guardaría en una tabla de tickets
    return {
        "ticket_id": str(ticket_id),
        "departamento": "SECRETARIA",  # podría determinarse por la intención
        "contexto_resumido": f"Motivo: {motivo}. Último mensaje: {contexto.get('historial', [])[-1] if contexto.get('historial') else ''}",
        "tiempo_estimado": "15 minutos"
    }