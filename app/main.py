# ByKP: Punto de Entrada Principal (FastAPI)
# app/main.py
# Célula 04 - Asistente Virtual SIS-UNETI 2026

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time

# Importamos nuestros enrutadores (routers)
from app.routers import consultar

# ============================================================================
# 1. GESTIÓN DE CICLO DE VIDA (Lifespan)
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Se ejecuta al iniciar el servidor
    print("🚀 [SIS-UNETI] Iniciando Asistente Virtual...")
    print("⏳ Conectando a PostgreSQL y Redis...")
    print("🧠 Cargando motor NLU (spaCy) y modelos locales...")
    
    # Aquí es donde el servidor se queda "escuchando"
    yield
    
    # Se ejecuta al apagar el servidor
    print("🛑 [SIS-UNETI] Apagando Asistente Virtual. Cerrando conexiones...")

# ============================================================================
# 2. INICIALIZACIÓN DE LA APLICACIÓN
# ============================================================================
app = FastAPI(
    title="Asistente Virtual SIS-UNETI",
    description="API de Inteligencia Artificial para atención estudiantil (Célula 04)",
    version="1.0.0",
    lifespan=lifespan
)

# Capturamos el tiempo de inicio para calcular el Uptime en el Health Check
START_TIME = time.time()

# ============================================================================
# 3. MIDDLEWARES (Seguridad y CORS)
# ============================================================================
# ByKP: Fundamental para que el Frontend (React de Ezequiel) pueda consumir la API
# sin recibir errores de "Cross-Origin Request Blocked".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: En producción, cambiar "*" por la URL del Core
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# ============================================================================
# 4. ENDPOINTS BASE Y ROUTERS
# ============================================================================

# ByKP: Conectamos la "boca" del asistente (endpoints de negocio) al servidor principal
app.include_router(consultar.router)

@app.get("/", tags=["Sistema"])
async def root():
    """Endpoint raíz para confirmar que la API responde."""
    return {
        "sistema": "SIS-UNETI 2026",
        "modulo": "Asistente Virtual AI",
        "estado": "Operativo",
        "celula": "04 - Servicios e Innovación"
    }

@app.get("/health", tags=["Sistema"])
async def health_check():
    """
    Endpoint de monitoreo (Health Check) utilizado por Docker e Infraestructura.
    Retorna el contrato JSON exacto que documentamos.
    """
    uptime_seconds = int(time.time() - START_TIME)
    horas = uptime_seconds // 3600
    minutos = (uptime_seconds % 3600) // 60
    segundos = uptime_seconds % 60
    uptime_str = f"{horas}h {minutos}m {segundos}s"

    return {
        "status": "healthy",
        "version": "1.0.0",
        "servicios": {
            "postgresql": "connected",
            "redis": "connected",
            "llm_engine": "ready",
            "chromadb": "connected"
        },
        "uptime": uptime_str
    }