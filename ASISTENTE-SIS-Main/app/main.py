from fastapi import FastAPI
from app.api.endpoints import query
from app.api.endpoints import admin_faq
from app.core.database import engine
from app.models import orm

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Crear tablas (si no existen)
orm.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Asistente Virtual UNETI", version="1.0.0")

# Montar archivos estáticos
static_path = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

app.include_router(query.router, prefix="/api/v1/asistente-virtual", tags=["Asistente"])
app.include_router(admin_faq.router, prefix="/api/v1/admin/faq", tags=["Admin FAQ"])

@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_path, "index.html"))

@app.get("/health")
def health_check():
    return {"status": "ok"}