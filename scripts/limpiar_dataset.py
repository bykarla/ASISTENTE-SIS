import json
import os
import unicodedata

# Rutas de archivos
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
INPUT_FILE = os.path.join(DATA_DIR, 'FAQs_Completo.json')
OUTPUT_FILE = os.path.join(DATA_DIR, 'FAQs_Saneado.json')

def normalizar_texto(texto):
    """Elimina acentos y pasa a minúsculas para una búsqueda exacta."""
    if not texto: return ""
    texto = texto.lower()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# DICCIONARIO MAESTRO: "palabra_clave_sin_acentos": ("Subcategoría", Prioridad)
# Ordenado de lo más urgente a lo menos urgente
REGLAS_MAESTRAS = {
    # 1. ACCESO Y BLOQUEOS (PRIORIDAD 10 - CRÍTICO)
    "clave": ("Recuperación de Acceso", 10),
    "contraseña": ("Recuperación de Acceso", 10),
    "credenciales": ("Recuperación de Acceso", 10),
    "acceso": ("Recuperación de Acceso", 10),
    "ingresar": ("Recuperación de Acceso", 10),
    "entrar": ("Recuperación de Acceso", 10),
    "usuario": ("Recuperación de Acceso", 10),
    "bloqueado": ("Recuperación de Acceso", 10),

    # 2. FALLAS DE PLATAFORMA Y DATOS ERRÓNEOS (PRIORIDAD 9 - ALTO)
    "duplicada": ("Soporte Plataforma", 9),
    "repetida": ("Soporte Plataforma", 9),
    "error en pnf": ("Corrección de Datos", 9),
    "pnf equivocado": ("Corrección de Datos", 9),
    "no aparecen": ("Soporte Plataforma", 9),
    "no me salen": ("Soporte Plataforma", 9),
    "no me cargaron": ("Soporte Plataforma", 9),
    "vacio": ("Soporte Plataforma", 9),
    "error": ("Soporte Plataforma", 9),
    "falla": ("Soporte Plataforma", 9),
    "plataforma": ("Soporte Plataforma", 9),
    "cambio de pnf": ("Corrección de Datos", 9),
    "cambio de carrera": ("Corrección de Datos", 9),

    # 3. TRÁMITES ACADÉMICOS CRÍTICOS (PRIORIDAD 9)
    "reingreso": ("Reingresos", 9),
    "reincorporacion": ("Reingresos", 9),
    "retomar": ("Reingresos", 9),
    "congelar": ("Retiros y Congelamientos", 9),
    "retiro": ("Retiros y Congelamientos", 9),
    "pausar": ("Retiros y Congelamientos", 9),

    # 4. GESTIÓN DE NOTAS Y MATERIAS (PRIORIDAD 8)
    "nota": ("Gestión de Calificaciones", 8),
    "calificacion": ("Gestión de Calificaciones", 8),
    "uc": ("Carga Académica", 8),
    "materia": ("Carga Académica", 8),
    "recursar": ("Carga Académica", 8),
    "reprobo": ("Carga Académica", 8),
    "reprobe": ("Carga Académica", 8),
    "verano": ("Cursos Intensivos", 8),
    "intensivo": ("Cursos Intensivos", 8),
    "equivalencia": ("Equivalencias", 8),

    # 5. PROYECTOS, PASANTÍAS Y GRADO (PRIORIDAD 8)
    "pasantia": ("Prácticas Profesionales", 8),
    "servicio comunitario": ("Servicio Comunitario", 8),
    "proyecto": ("Proyecto Sociotecnológico", 8),
    "titulo": ("Egresados y Titulación", 8),
    "grado": ("Egresados y Titulación", 8),
    "tecnico medio": ("Egresados y Titulación", 8),

    # 6. DOCUMENTACIÓN (PRIORIDAD 7)
    "constancia": ("Solicitud de Documentos", 7),
    "record": ("Solicitud de Documentos", 7),
    "certificado": ("Solicitud de Documentos", 7),
    "carnet": ("Carnetización", 7),

    # 7. ADMISIÓN (PRIORIDAD 7)
    "opsu": ("Admisión", 7),
    "sni": ("Admisión", 7),
    "cupo": ("Admisión", 7),
    "inscripcion": ("Inscripciones", 7),

    # 8. DUDAS GENERALES E INFORMATIVAS (PRIORIDAD 5)
    "clases": ("Información Académica", 5),
    "comienzo": ("Información Académica", 5),
    "inicio": ("Información Académica", 5),
    "telegram": ("Comunidad y Grupos", 4),
    "whatsapp": ("Comunidad y Grupos", 4),
    "grupo": ("Comunidad y Grupos", 4)
}

def sanear_dataset_ninja():
    print(f"🚀 Iniciando procesamiento Ninja de {INPUT_FILE}...")
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sub_modificadas = 0
    prio_modificadas = 0
    pendientes_restantes = 0
    
    for item in data:
        pregunta_original = item.get("pregunta_patron", "")
        # Normalizamos la pregunta (sin acentos, en minúsculas)
        pregunta_norm = normalizar_texto(pregunta_original)
        
        # 1. Atacar los "Pendiente de Definir"
        if item.get("subcategoria") == "Pendiente de Definir":
            clasificado = False
            for clave, (nueva_sub, nueva_prio) in REGLAS_MAESTRAS.items():
                # Buscamos la clave normalizada en la pregunta normalizada
                if normalizar_texto(clave) in pregunta_norm:
                    item["subcategoria"] = nueva_sub
                    item["prioridad"] = nueva_prio
                    sub_modificadas += 1
                    clasificado = True
                    break
            
            if not clasificado:
                pendientes_restantes += 1
        
        # 2. Ajustar Prioridades (Criterio de Aceptación 2)
        # Si la prioridad es 5 (por defecto) o menor a la requerida por negocio
        else:
            for clave, (sub, nueva_prio) in REGLAS_MAESTRAS.items():
                if normalizar_texto(clave) in pregunta_norm:
                    if item.get("prioridad") != nueva_prio:
                        item["prioridad"] = nueva_prio
                        prio_modificadas += 1
                    break

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ Proceso completado exitosamente.")
    print(f"📊 Subcategorías 'Pendientes' resueltas: {sub_modificadas}")
    print(f"📊 Prioridades ajustadas por urgencia: {prio_modificadas}")
    print(f"⚠️ Registros que siguen 'Pendientes' (Casos muy raros): {pendientes_restantes}")
    print(f"💾 Resultado guardado en: {OUTPUT_FILE}")

if __name__ == "__main__":
    sanear_dataset_ninja()