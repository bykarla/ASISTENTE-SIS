import asyncio
import os
import sys

# Añadir el directorio raíz al path para importar módulos de la app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.core.redis_client import redis_client
from app.models.orm import AsistenteConocimiento
from app.core.config import settings

async def debug_connection():
    print("--- INICIANDO DIAGNÓSTICO DE CONEXIÓN ---")
    print(f"DATABASE_URL (desenmascarada): {settings.DATABASE_URL}")
    print(f"REDIS_URL: {settings.REDIS_URL}")
    print(f"OLLAMA_URL: {settings.OLLAMA_URL}")

    # 1. Probar Postgres
    print("\n1. Probando Postgres...")
    try:
        db = SessionLocal()
        # Intentar una consulta simple
        count = db.query(AsistenteConocimiento).count()
        print(f"   [OK] Conexión a Postgres exitosa. Registros en conocimiento: {count}")
        db.close()
    except Exception as e:
        print(f"   [ERROR] Fallo en Postgres: {e}")

    # 2. Probando Redis
    print("\n2. Probando Redis...")
    try:
        # Ping a Redis
        res = await redis_client.ping()
        print(f"   [OK] Conexión a Redis exitosa. PING: {res}")
    except Exception as e:
        print(f"   [ERROR] Fallo en Redis: {e}")

    # 3. Probando Ollama
    print("\n3. Probando Ollama...")
    import httpx
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{settings.OLLAMA_URL}/api/tags", timeout=5.0)
            if resp.status_code == 200:
                print(f"   [OK] Ollama es accesible. Modelos: {resp.json().get('models', 'no listados')}")
            else:
                print(f"   [AVISO] Ollama respondió con status {resp.status_code}")
    except Exception as e:
        print(f"   [ERROR] Fallo en Ollama: {e}")

    print("\n--- DIAGNÓSTICO FINALIZADO ---")

if __name__ == "__main__":
    asyncio.run(debug_connection())
