FROM python:3.10

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc g++ build-essential python3-dev libsndfile1 ffmpeg libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Actualizar pip, setuptools y wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt .

# Instalar numpy primero (para evitar conflictos)
RUN pip install --no-cache-dir "numpy<2"

# Luego instalar el resto de dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Descargar modelo de spaCy
RUN python -m spacy download es_core_news_sm

# Copiar el código de la aplicación
COPY ./app /app/app

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]