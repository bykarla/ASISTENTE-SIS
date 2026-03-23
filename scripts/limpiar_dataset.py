import json
import os

# Rutas de archivos
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
INPUT_FILE = os.path.join(DATA_DIR, 'FAQs_Completo.json')
OUTPUT_FILE = os.path.join(DATA_DIR, 'FAQs_Saneado.json')

# REGLAS MAESTRAS DE NEGOCIO (Subcategoría, Prioridad)
REGLAS_MAESTRAS = {
    # PRIORIDAD 10: Críticos / Bloqueantes
    "acceso": ("Recuperación de Acceso", 10),
    "contraseña": ("Recuperación de Acceso", 10),
    "clave": ("Recuperación de Acceso", 10),
    "entrar": ("Recuperación de Acceso", 10),
    "password": ("Recuperación de Acceso", 10),
    "login": ("Recuperación de Acceso", 10),
    "error": ("Soporte Técnico", 10),
    "caida": ("Soporte Técnico", 10),
    "no carga": ("Soporte Técnico", 10),

    # PRIORIDAD 8: Procesos de ingreso
    "inscripción": ("Admisión", 8),
    "censo": ("Admisión", 8),
    "preinscripción": ("Admisión", 8),
    "documentos": ("Documentación", 8),
    "requisitos": ("Documentación", 8),
    "titulo": ("Documentación", 8),

    # PRIORIDAD 6: Gestión Académica
    "nota": ("Gestión Académica", 6),
    "examen": ("Gestión Académica", 6),
    "evaluación": ("Gestión Académica", 6),
    "profesor": ("Gestión Académica", 6),
    "moodle": ("Plataforma Virtual", 6),
    "aula": ("Plataforma Virtual", 6),

    # PRIORIDAD 4: Informativos
    "uneti": ("Información Institucional", 4),
    "ubicación": ("Información Institucional", 4),
    "horario": ("Información Institucional", 5),
    "donde": ("Información Institucional", 4)
}

def sanear_dataset_pro():
    print(f"🚀 Iniciando procesamiento avanzado de {INPUT_FILE}...")
    
    if not os.path.exists(INPUT_FILE):
        print("❌ Error: No se encuentra el archivo fuente.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sub_modificadas = 0
    prio_modificadas = 0
    
    for item in data:
        pregunta = item.get("pregunta_patron", "").lower()
        
        # 1. Resolver Subcategorías "Pendientes"
        if item.get("subcategoria") == "Pendiente de Definir":
            for clave, (nueva_sub, nueva_prio) in REGLAS_MAESTRAS.items():
                if clave in pregunta:
                    item["subcategoria"] = nueva_sub
                    item["prioridad"] = nueva_prio # Asignamos prioridad acorde
                    sub_modificadas += 1
                    break
        
        # 2. Ajustar Prioridades Estáticas (si son "5" o por defecto)
        # Esto cumple con el requerimiento de no dejar todo en prioridad plana
        for clave, (sub, nueva_prio) in REGLAS_MAESTRAS.items():
            if clave in pregunta:
                if item.get("prioridad") != nueva_prio:
                    item["prioridad"] = nueva_prio
                    prio_modificadas += 1
                break

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ Proceso completado exitosamente.")
    print(f"📊 Subcategorías definidas: {sub_modificadas}")
    print(f"📊 Prioridades ajustadas: {prio_modificadas}")
    print(f"💾 Resultado guardado en: {OUTPUT_FILE}")

if __name__ == "__main__":
    sanear_dataset_pro()