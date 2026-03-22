# ByKP: Punto de Entrada Principal (FastAPI)
# app/main.py
# Célula 04 - Asistente Virtual SIS-UNETI 2026

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import time
import psycopg2
import os
from redis import Redis

# Importamos nuestros enrutadores (routers)
from app.routers import consultar, escalar
from app.dependencies import get_db, get_redis
from app.config import settings

# ============================================================================
# 1. GESTIÓN DE CICLO DE VIDA (Lifespan)
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Se ejecuta al iniciar el servidor
    print(f"🚀 [{settings.PROJECT_NAME}] Iniciando Asistente Virtual v{settings.VERSION}...")
    yield
    # Se ejecuta al apagar el servidor
    print(f"🛑 [{settings.PROJECT_NAME}] Apagando Asistente Virtual...")

# ============================================================================
# 2. INICIALIZACIÓN DE LA APLICACIÓN
# ============================================================================
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API de Inteligencia Artificial para atención estudiantil (Célula 04)",
    version=settings.VERSION,
    lifespan=lifespan
)

# --- Configuración de Archivos Estáticos ---
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


START_TIME = time.time()

# ============================================================================
# 3. MIDDLEWARES (Seguridad y CORS)
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# ============================================================================
# 4. ENDPOINTS BASE Y ROUTERS
# ============================================================================

app.include_router(consultar.router)
app.include_router(escalar.router)

@app.get("/", tags=["Sistema"])
async def root():
    """Sirve la interfaz del Asistente Virtual."""
    index_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "sistema": "SIS-UNETI 2026",
        "modulo": "Asistente Virtual AI",
        "estado": "Operativo (Frontend no encontrado)",
        "celula": "04 - Servicios e Innovación"
    }


@app.get("/health", tags=["Sistema"])
async def health_check():
    """
    Endpoint de monitoreo (Health Check) real.
    """
    uptime_seconds = int(time.time() - START_TIME)
    
    # Verificación Real PostgreSQL
    db_status = "disconnected"
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        conn.close()
        db_status = "connected"
    except Exception:
        pass

    # Verificación Real Redis
    redis_status = "disconnected"
    try:
        r = Redis.from_url(settings.REDIS_URL)
        r.ping()
        redis_status = "connected"
    except Exception:
        pass

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "version": settings.VERSION,
        "servicios": {
            "postgresql": db_status,
            "redis": redis_status,
            "llm_engine": "ready" if settings.LLM_API_KEY else "not_configured",
        },
        "uptime": f"{uptime_seconds}s"
    }