# ByKP: Dockerfile para el Asistente Virtual SIS-UNETI
# Célula 04 - SIS-UNETI 2026

# Usamos una imagen completa de Python (incluye build tools)
FROM python:3.11

# Evitar que Python genere archivos .pyc y permitir logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo
WORKDIR /app

# Solo instalamos libpq-dev para psycopg2 (aunque probablemente ya esté en la imagen completa)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalamos las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Descargamos el modelo de spaCy (necesario para Phase 2/NLU)
RUN python -m spacy download es_core_news_sm

# Copiamos el resto del código
COPY . .

# Exponemos el puerto de FastAPI
EXPOSE 8000

# Comando para iniciar la aplicación con Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
