import httpx
from app.core.config import settings

class SISUnetiClient:
    def __init__(self):
        self.base_url = settings.SIS_CORE_URL
        self.client = httpx.AsyncClient(timeout=10.0)

    async def obtener_historial_academico(self, jwt: str, cedula: str = None):
        # Mock: devuelve datos de ejemplo
        # En realidad llamaría a GET /estudiante/historial-academico
        return {
            "notas": [
                {"materia": "Programación I", "nota_100": 75, "nota_20": 15},
                {"materia": "Base de Datos", "nota_100": 82, "nota_20": 16.4}
            ]
        }

    async def obtener_estatus_tramite(self, jwt: str, tramite_id: str):
        return {"estado": "en_proceso", "observaciones": "Revisión de documentos"}

    # ... otros métodos según necesidad