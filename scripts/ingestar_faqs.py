# ByKP: Script de Ingesta de Base de Conocimiento (Capa 1)
# Lee el dataset faqs.json, valida con Pydantic e inserta en PostgreSQL.
# Célula 04: Servicios e Innovación - SIS-UNETI 2026

import json
import os
import sys
import psycopg2
from pydantic import ValidationError
from dotenv import load_dotenv

# Añadimos la raíz del proyecto al path para poder importar los schemas de 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas import ConocimientoCreate

# Cargar variables de entorno (ej. DATABASE_URL)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# ByKP: Ruta actualizada al nuevo archivo validado por QA (Issue #2)
JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'FAQs_Saneado.json')

def ingestar_datos():
    print("🚀 [SIS-UNETI] Iniciando ingesta del Dataset Consolidado (FAQs_Completo)...")
    
    # 1. Verificar si existe el archivo JSON
    if not os.path.exists(JSON_PATH):
        print(f"❌ Error: No se encontró el archivo en {JSON_PATH}")
        return

    # 2. Cargar los datos crudos del JSON
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        try:
            faqs_crudas = json.load(f)
            print(f"📂 Archivo cargado exitosamente. Total registros crudos: {len(faqs_crudas)}")
        except json.JSONDecodeError as e:
            print(f"❌ Error leyendo el JSON: {e}")
            return

    # 3. Conectar a PostgreSQL
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Error: Variable de entorno DATABASE_URL no definida.")
        return

    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        print("✅ Conexión a PostgreSQL establecida.")
        
        # ByKP: TRUNCATE limpia la tabla antes de insertar para evitar duplicidad de FAQs viejas
        print("🧹 Limpiando registros anteriores en la base de datos...")
        cursor.execute("TRUNCATE TABLE asistente_virtual.asistente_conocimiento RESTART IDENTITY CASCADE;")
        
        # 4. Procesamiento, Validación Pydantic e Inserción
        registros_insertados = 0
        registros_fallidos = 0

        for idx, item in enumerate(faqs_crudas):
            try:
                # ¡ Aquí Pydantic valida los tipos de datos estrictamente
                faq_validada = ConocimientoCreate(**item)
                
                # Preparamos el query SQL respetando el schema "asistente_virtual" de Josua
                query = """
                    INSERT INTO asistente_virtual.asistente_conocimiento 
                    (categoria, subcategoria, pregunta_patron, palabras_clave, respuesta, acceso_publico, prioridad, activo, creado_por)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Ejecutamos la inserción. psycopg2 convierte automáticamente la lista de tags a un array de Postgres
                cursor.execute(query, (
                    faq_validada.categoria,
                    faq_validada.subcategoria,
                    faq_validada.pregunta_patron,
                    faq_validada.tags, # Pydantic ya mapeó 'palabras_clave' a 'tags'
                    faq_validada.respuesta,
                    faq_validada.acceso_publico,
                    faq_validada.prioridad,
                    faq_validada.activo,
                    "sistema_ingesta_bykp"
                ))
                registros_insertados += 1
                
            except ValidationError as ve:
                print(f"⚠️ Error de validación Pydantic en registro {idx+1}: {ve}")
                registros_fallidos += 1
            except Exception as e:
                print(f"⚠️ Error insertando registro {idx+1} en BD: {e}")
                registros_fallidos += 1
                conn.rollback() # Revertimos solo esta transacción si falla la BD

        # Confirmamos los cambios en la base de datos
        conn.commit()
        
        print("\n📊 --- RESUMEN DE INGESTA ---")
        print(f"✅ Registros insertados: {registros_insertados}")
        print(f"❌ Registros fallidos: {registros_fallidos}")
        print("----------------------------")

    except psycopg2.Error as db_err:
        print(f"❌ Error de base de datos crítico: {db_err}")
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()
            print("🔌 Conexión a BD cerrada.")

if __name__ == "__main__":
    ingestar_datos()