import json
import os
import unicodedata

# [PASO 1]: Configuración de rutas de archivos
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
INPUT_FILE = os.path.join(DATA_DIR, 'FAQs_Completo.json')
OUTPUT_FILE = os.path.join(DATA_DIR, 'FAQs_Saneado.json')

def normalizar_texto(texto):
    """[PASO 2]: Limpieza de texto para evitar fallos por acentos o mayúsculas."""
    if not texto: return ""
    texto = texto.lower()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# [PASO 3]: Diccionario Maestro de Reglas de Negocio (Subcategoría, Prioridad)
# Basado en la auditoría de registros orgánicos reales
REGLAS_MAESTRAS = {
    # PRIORIDAD 10: Bloqueantes y Soporte de Acceso
    "clave": ("Recuperación de Acceso", 10),
    "contraseña": ("Recuperación de Acceso", 10),
    "credencial": ("Recuperación de Acceso", 10),
    "acceso": ("Recuperación de Acceso", 10),
    "ingresar": ("Recuperación de Acceso", 10),
    "usuario": ("Recuperación de Acceso", 10),
    "correo": ("Soporte Técnico", 10),
    "email": ("Soporte Técnico", 10),

    # PRIORIDAD 9: Trámites de Permanencia y Errores Críticos
    "reintegro": ("Reingresos", 9),
    "reincorporacion": ("Reingresos", 9),
    "inactividad": ("Reingresos", 9),
    "congelar": ("Retiros y Congelamientos", 9),
    "retiro": ("Retiros y Congelamientos", 9),
    "error": ("Soporte Plataforma", 9),
    "falla": ("Soporte Plataforma", 9),
    "no aparecen": ("Soporte Plataforma", 9),
    "cambio de pnf": ("Corrección de Datos", 9),

    # PRIORIDAD 8: Gestión Académica y Avance
    "nota": ("Gestión de Calificaciones", 8),
    "parcial": ("Gestión Académica", 8),
    "profesor": ("Gestión Académica", 8),
    "docente": ("Gestión Académica", 8),
    "semestre": ("Carga Académica", 8),
    "avanzar": ("Carga Académica", 8),
    "unidades de credito": ("Carga Académica", 8),
    "uc": ("Carga Académica", 8),
    "moodle": ("Plataforma Virtual", 6),
    "proyecto": ("Proyecto Sociotecnológico", 8),

    # PRIORIDAD 7: Ingreso y Documentos
    "inscripcion": ("Inscripciones", 7),
    "censo": ("Admisión", 7),
    "opsu": ("Admisión", 7),
    "profesional": ("Admisión", 8),
    "constancia": ("Solicitud de Documentos", 7),
    "titulo": ("Egresados y Titulación", 8),

    # PRIORIDAD 4-5: Información y Cortesía
    "carreras": ("Oferta Académica", 4),
    "oferta": ("Oferta Académica", 4),
    "clases": ("Información Académica", 5),
    "hola": ("Saludo / General", 2),
    "buen dia": ("Saludo / General", 2)
}

def sanear_dataset_final():
    """[PASO 4]: Ejecución del motor de búsqueda y reemplazo."""
    print(f"🚀 Iniciando procesamiento Final de {INPUT_FILE}...")
    
    if not os.path.exists(INPUT_FILE):
        print("❌ Error: No se encuentra el archivo fuente.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sub_modificadas = 0
    prio_modificadas = 0
    pendientes_restantes = 0
    
    for item in data:
        pregunta_norm = normalizar_texto(item.get("pregunta_patron", ""))
        
        # Lógica de clasificación
        clasificado = False
        for clave, (nueva_sub, nueva_prio) in REGLAS_MAESTRAS.items():
            if normalizar_texto(clave) in pregunta_norm:
                # Solo cambiamos subcategoría si está pendiente
                if item.get("subcategoria") == "Pendiente de Definir":
                    item["subcategoria"] = nueva_sub
                    sub_modificadas += 1
                
                # Siempre actualizamos prioridad si es distinta a la de la regla
                if item.get("prioridad") != nueva_prio:
                    item["prioridad"] = nueva_prio
                    prio_modificadas += 1
                
                clasificado = True
                break
        
        if not clasificado and item.get("subcategoria") == "Pendiente de Definir":
            pendientes_restantes += 1

    # [PASO 5]: Persistencia de datos saneados
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ Proceso completado exitosamente.")
    print(f"📊 Subcategorías resueltas: {sub_modificadas}")
    print(f"📊 Prioridades optimizadas: {prio_modificadas}")
    print(f"⚠️ Registros residuales: {pendientes_restantes}")
    print(f"💾 Archivo final: {OUTPUT_FILE}")

if __name__ == "__main__":
    sanear_dataset_final()