import json
import os
import unicodedata

# Rutas de archivos
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
INPUT_FILE = os.path.join(DATA_DIR, 'FAQs_Completo.json')
OUTPUT_FILE = os.path.join(DATA_DIR, 'FAQs_Saneado.json')

def normalizar_texto(texto):
    """Elimina acentos y estandariza para búsqueda."""
    if not texto: return ""
    texto = texto.lower()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# DICCIONARIO MAESTRO FINAL - COBERTURA 100%
REGLAS_MAESTRAS = {
    # PRIORIDAD 10: ACCESO Y URGENCIA
    "clave": ("Recuperación de Acceso", 10),
    "contrase": ("Recuperación de Acceso", 10),
    "acceso": ("Recuperación de Acceso", 10),
    "ingres": ("Recuperación de Acceso", 10),
    "login": ("Recuperación de Acceso", 10),
    "plataforma": ("Soporte Técnico", 10),
    "no me permite": ("Soporte Técnico", 10),
    "urgente": ("Soporte Técnico", 10),
    "respuesta": ("Soporte Técnico", 10),

    # PRIORIDAD 9: TRÁMITES Y CAMBIOS (PNF / REINGRESO)
    "reingreso": ("Reingresos", 9),
    "retomar": ("Reingresos", 9),
    "reincorpor": ("Reingresos", 9),
    "reintegro": ("Reingresos", 9),
    "pnf": ("Corrección de Datos", 9),
    "incorrecto": ("Corrección de Datos", 9),
    "modificacion": ("Corrección de Datos", 9),
    "cambio": ("Corrección de Datos", 9),
    "retiro": ("Retiros y Congelamientos", 9),
    "retirarme": ("Retiros y Congelamientos", 9),
    "me retiro": ("Retiros y Congelamientos", 9),

    # PRIORIDAD 8: ACADÉMICO, EVALUACIÓN Y ACREDITACIÓN
    "acreditacion": ("Acreditación de Saberes", 8),
    "experiencia": ("Acreditación de Saberes", 8),
    "saber": ("Acreditación de Saberes", 8),
    "evaluaci": ("Gestión Académica", 8),
    "examen": ("Gestión Académica", 8),
    "prueba": ("Gestión Académica", 8),
    "cuestionario": ("Gestión Académica", 8),
    "denuncia": ("Gestión Académica", 8),
    "nota": ("Gestión de Calificaciones", 8),
    "reparaci": ("Gestión de Calificaciones", 8),
    "recuperaci": ("Gestión de Calificaciones", 8),
    "materia": ("Carga Académica", 8),
    "unidad": ("Carga Académica", 8),
    "programaci": ("Carga Académica", 8),
    "matematica": ("Carga Académica", 8),
    "ingles": ("Carga Académica", 8),
    "taller": ("Carga Académica", 8),
    "horaria": ("Carga Académica", 8),
    "tarea": ("Carga Académica", 8),

    # PRIORIDAD 7: ADMISIÓN Y DOCUMENTOS
    "postulaci": ("Solicitud de Documentos", 7),
    "carta": ("Solicitud de Documentos", 7),
    "certific": ("Solicitud de Documentos", 7),
    "inscrit": ("Inscripciones", 7),
    "pre-inscri": ("Inscripciones", 7),
    "cantv": ("Inscripciones", 7),
    "opsu": ("Admisión", 7),
    "osup": ("Admisión", 7), # Por el error de dedo en tu lista
    "estudiantil": ("Información Académica", 5),
    "estudio": ("Información Académica", 5),
    "pemsun": ("Información Académica", 5),
    "pensum": ("Información Académica", 5),

    # PRIORIDAD 4-6: CARRERAS Y CONSULTAS
    "informatica": ("Oferta Académica", 4),
    "telecomunicac": ("Oferta Académica", 4),
    "enfermeria": ("Oferta Académica", 4),
    "satelital": ("Oferta Académica", 4),
    "licenciatura": ("Oferta Académica", 4),
    "especializac": ("Oferta Académica", 4),
    "consulta": ("Información General", 5),
    "estatus": ("Información General", 5),
    "notificac": ("Información General", 5),
    "paso siguiente": ("Información General", 5)
}

def sanear_dataset_total():
    print(f"🚀 Ejecutando barrido final en {INPUT_FILE}...")
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sub_modificadas = 0
    
    for item in data:
        pregunta_norm = normalizar_texto(item.get("pregunta_patron", ""))
        
        # 1. Intentamos clasificar
        clasificado = False
        for clave, (nueva_sub, nueva_prio) in REGLAS_MAESTRAS.items():
            if normalizar_texto(clave) in pregunta_norm:
                item["subcategoria"] = nueva_sub
                item["prioridad"] = nueva_prio
                sub_modificadas += 1
                clasificado = True
                break
        
        # 2. SEGURO ANTI-PENDIENTES: Si nada funcionó, asignamos categoría general
        if not clasificado and item.get("subcategoria") == "Pendiente de Definir":
            item["subcategoria"] = "Atención por Clasificar"
            item["prioridad"] = 5
            sub_modificadas += 1

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ Saneamiento EXITOSO.")
    print(f"📊 Total registros procesados/limpios: {sub_modificadas}")
    print(f"💾 Archivo generado: {OUTPUT_FILE}")

if __name__ == "__main__":
    sanear_dataset_total()