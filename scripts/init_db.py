# ByKP: Inicializador de Base de Datos
# Lee el archivo .sql y crea las tablas en PostgreSQL
import os
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL_PATH = os.path.join(BASE_DIR, 'database', 'schema_asistente_virtual.sql')

def inicializar_bd():
    print("🚀 [SIS-UNETI] Iniciando migración de Base de Datos...")
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        print("❌ Error: DATABASE_URL no encontrada en el archivo .env")
        return

    try:
        # Conectar a Postgres (Docker)
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Leer el archivo SQL
        with open(SQL_PATH, 'r', encoding='utf-8') as file:
            sql_queries = file.read()
            
        # Ejecutar los queries
        cursor.execute(sql_queries)
        conn.commit()
        
        print("✅ ¡Tablas e índices creados exitosamente en PostgreSQL!")
        
    except Exception as e:
        print(f"❌ Error al crear las tablas: {e}")
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    inicializar_bd()