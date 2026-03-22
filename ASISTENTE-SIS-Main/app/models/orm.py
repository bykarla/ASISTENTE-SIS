from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, JSON, ForeignKey, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class AsistenteSesion(Base):
    __tablename__ = "asistente_sesiones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    estudiante_id = Column(UUID(as_uuid=True), nullable=True)  # referencia a usuarios.id
    fecha_inicio = Column(DateTime, server_default=func.now())
    fecha_fin = Column(DateTime, nullable=True)
    estado = Column(String(15), default='ACTIVA')  # ACTIVA, CERRADA, ESCALADA
    capa_maxima_usada = Column(Integer, nullable=True)
    satisfaccion_usuario = Column(Integer, nullable=True)  # 1-5

class AsistenteMensaje(Base):
    __tablename__ = "asistente_mensajes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sesion_id = Column(UUID(as_uuid=True), ForeignKey("asistente_sesiones.id"))
    rol = Column(String(10))  # USUARIO, ASISTENTE, HUMANO
    contenido = Column(Text)
    intencion_detectada = Column(String(50), nullable=True)
    capa_respuesta = Column(Integer, nullable=True)
    confianza = Column(Numeric(3,2), nullable=True)
    timestamp = Column(DateTime, server_default=func.now())

class AsistenteConocimiento(Base):
    __tablename__ = "asistente_conocimiento"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    categoria = Column(String(50), nullable=False)
    pregunta_patron = Column(Text, nullable=False)
    palabras_clave = Column(JSON, nullable=False)  # lista de strings
    respuesta = Column(Text, nullable=False)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())