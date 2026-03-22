import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal
from app.models.orm import AsistenteConocimiento

FAQS = [
    {
        "categoria": "inscripciones",
        "pregunta_patron": "¿Cuándo abren las inscripciones?",
        "palabras_clave": ["inscripciones", "abren", "fecha"],
        "respuesta": "Las inscripciones para el periodo 2026-II abren el 15 de septiembre. Puedes realizarlas a través del SIS-UNETI."
    },
    {
        "categoria": "notas",
        "pregunta_patron": "¿Cómo veo mis notas?",
        "palabras_clave": ["notas", "ver", "calificaciones"],
        "respuesta": "Puedes ver tus notas en el módulo 'Historial Académico' del SIS-UNETI. Las notas de Moodle se convierten automáticamente a escala 1-20."
    },
    {
        "categoria": "carnet",
        "pregunta_patron": "¿Cómo genero mi carnet digital?",
        "palabras_clave": ["carnet", "generar", "digital"],
        "respuesta": "Dirígete a la sección 'Carnet Digital' en el SIS. Allí podrás descargar tu carnet con código QR."
    },

    {
        "categoria": "requisitos",
        "pregunta_patron": "¿Cuáles son los requisitos y documentos para inscribirse?",
        "palabras_clave": ["requisitos", "documentos", "inscripciones"],
        "respuesta": "Para formalizar tu inscripción debes traer en una carpeta marrón tamaño oficio:" 
                      "Planilla de asignación OPSU o Censo Interno."
                      "Cédula de identidad laminada y copia ampliada."
                      "Título de Bachiller (Original y copia fondo negro)."
                      "Notas certificadas de 1er a 5to año."
                      "Partida de nacimiento original."
                      "2 fotos tipo carnet."
    },
    # ... agregar más
]

def seed():
    db = SessionLocal()
    for faq in FAQS:
        existe = db.query(AsistenteConocimiento).filter(AsistenteConocimiento.pregunta_patron == faq["pregunta_patron"]).first()
        if not existe:
            db.add(AsistenteConocimiento(**faq))
    db.commit()
    db.close()
    print("FAQs cargadas.")

if __name__ == "__main__":
    seed()