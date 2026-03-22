# ByKP: Inyección de Dependencias
# app/dependencies.py
# Célula 04 - Asistente Virtual SIS-UNETI

import psycopg2
from psycopg2.extras import RealDictCursor
from redis import Redis
from app.config import settings

def get_db():
    """
    Generador para obtener una conexión a PostgreSQL.
    Se asegura de cerrar la conexión después de usarla.
    """
    conn = None
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        yield conn
    except Exception as e:
        print(f"❌ Error de conexión a DB: {e}")
        raise e
    finally:
        if conn:
            conn.close()

def get_redis():
    """
    Retorna un cliente de Redis conectado.
    """
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)
