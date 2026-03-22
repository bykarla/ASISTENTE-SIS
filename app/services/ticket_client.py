# ByKP: Cliente de Tickets (Simulación Capa 3)
# app/services/ticket_client.py
# Célula 04 - Asistente Virtual SIS-UNETI

import uuid
from datetime import datetime
from app.schemas import EscalarRequest

async def crear_ticket_soporte(db_conn, request: EscalarRequest):
    """
    Simula la creación de un ticket. 
    En esta fase MVP, lo guardamos en los logs y devolvemos un ID ficticio.
    """
    ticket_id = str(uuid.uuid4())
    
    # ByKP: Aquí iría la lógica para insertar en la tabla de escalados de PostgreSQL
    # si existiera en el esquema (el esquema actual solo tiene 'asistente_conocimiento').
    # Por ahora, simulamos éxito.
    
    print(f"🎫 [TICKET] Nuevo escalado creado: {ticket_id}")
    print(f"📝 Motivo: {request.motivo_escalado}")
    
    return {
        "ticket_id": ticket_id,
        "status": "creado",
        "mensaje": "Tu solicitud ha sido enviada a Control de Estudios. Un operador te contactará pronto.",
        "fecha_creacion": datetime.now()
    }
