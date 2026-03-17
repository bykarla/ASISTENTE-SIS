-- ByKP: Esquema de Base de Datos para el Asistente Virtual
-- Célula 04 - SIS-UNETI 2026

-- 1. Crear el esquema aislado por seguridad
CREATE SCHEMA IF NOT EXISTS asistente_virtual;

-- 2. Habilitar la extensión para generar UUIDs automáticamente
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 3. Crear la tabla de Conocimiento (Capa 1 - FAQs)
CREATE TABLE IF NOT EXISTS asistente_virtual.asistente_conocimiento (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    categoria VARCHAR(50) NOT NULL,
    subcategoria VARCHAR(50),
    pregunta_patron TEXT NOT NULL,
    palabras_clave TEXT[] NOT NULL, -- Arreglo de strings para los tags
    respuesta TEXT NOT NULL,
    acceso_publico BOOLEAN DEFAULT TRUE,
    prioridad INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    veces_utilizada INTEGER DEFAULT 0,
    version INTEGER DEFAULT 1,
    creado_por VARCHAR(100),
    aprobado_por VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Crear un índice GIN para búsquedas ultra-rápidas en los tags (Requisito del Tech Lead)
CREATE INDEX IF NOT EXISTS idx_conocimiento_tags 
ON asistente_virtual.asistente_conocimiento USING GIN (palabras_clave);