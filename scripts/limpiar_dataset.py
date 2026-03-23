import json
import os

# Rutas de archivos
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
INPUT_FILE = os.path.join(DATA_DIR, 'FAQs_Completo.json')
OUTPUT_FILE = os.path.join(DATA_DIR, 'FAQs_Saneado.json')

# Diccionario de Mapeo Semántico (Reglas de Negocio)
# Si detecta la 'palave_clave' en la pregunta, asigna la 'subcategoria'
MAPEO_SUBCATEGORIAS = {
    "acceso": "Recuperación de Acceso",
    "contraseña": "Recuperación de Acceso",
    "password": "Recuperación de Acceso",
    "usuario": "Recuperación de Acceso",
    "evaluación": "Gestión Académica",
    "nota": "Gestión Académica",
    "examen": "Gestión Académica",
    "inscripción": "Admisión",
    "censo": "Admisión",
    "requisitos": "Documentación",
    "moodle": "Plataforma Virtual"
}

def sanear_subcategorias():
    print(f"🔍 Iniciando saneamiento de {INPUT_FILE}...")
    
    if not os.path.exists(INPUT_FILE):
        print("❌ Error: No se encuentra el archivo fuente.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    modificados = 0
    
    for item in data:
        # Solo actuamos si está pendiente
        if item.get("subcategoria") == "Pendiente de Definir":
            pregunta = item.get("pregunta_patron", "").lower()
            
            # Buscamos coincidencia en nuestro diccionario de reglas
            for clave, nueva_sub in MAPEO_SUBCATEGORIAS.items():
                if clave in pregunta:
                    item["subcategoria"] = nueva_sub
                    modificados += 1
                    break # Asigna la primera coincidencia y salta al siguiente item

    # Guardamos el resultado en un nuevo archivo para no destruir el original (buena práctica de QA)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"✅ Saneamiento completado.")
    print(f"📊 Registros reclasificados: {modificados}")
    print(f"💾 Archivo guardado en: {OUTPUT_FILE}")

if __name__ == "__main__":
    sanear_subcategorias()