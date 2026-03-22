# ByKP: Endpoint de Escalado a Humano
# app/routers/escalar.py
# Célula 04 - Asistente Virtual SIS-UNETI

from fastapi import APIRouter, Depends
from app.schemas import EscalarRequest, EscalarResponse
from app.dependencies import get_db
from app.services.ticket_client import crear_ticket_soporte

router = APIRouter(prefix="/api/v1", tags=["Soporte"])

@router.post("/escalar", response_model=EscalarResponse)
async def escalar_solicitud(request: EscalarRequest, db = Depends(get_db)):
    """
    Recibe una solicitud de escalado y genera un ticket de atención.
    """
    resultado = await crear_ticket_soporte(db, request)
    
    return EscalarResponse(
        ticket_id=resultado["ticket_id"],
        status=resultado["status"],
        mensaje=resultado["mensaje"],
        fecha_creacion=resultado["fecha_creacion"]
    )
