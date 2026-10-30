# Dockerfile
# ERP Django con WeasyPrint
# Base: Python 3.11 sobre Debian Bookworm slim
# ─────────────────────────────────────────────────────────────────

# ── ETAPA 1: imagen base ─────────────────────────────────────────
FROM python:3.11-slim-bookworm AS base

# Evitar archivos .pyc y que Python bufferice la salida
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ── ETAPA 2: dependencias de sistema ─────────────────────────────
FROM base AS system-deps

RUN apt-get update && apt-get install -y --no-install-recommends \
    # ── Dependencias de WeasyPrint ──────────────────────────────
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libcairo-gobject2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
    # ── Fuentes adicionales para mejor tipografía ───────────────
    fonts-dejavu-core \
    # ── Dependencias para Pillow (imágenes en Django) ───────────
    libjpeg62-turbo-dev \
    libpng-dev \
    libwebp-dev \
    zlib1g-dev \
    # ── Cliente PostgreSQL (psycopg2) ───────────────────────────
    libpq-dev \
    gcc \
    # ── Herramientas de diagnóstico (se pueden eliminar en prod) ─
    curl \
 && rm -rf /var/lib/apt/lists/*    # limpiar caché de apt → imagen más pequeña

# ── ETAPA 3: dependencias Python ─────────────────────────────────
FROM system-deps AS python-deps

WORKDIR /app

# Copiar solo requirements primero para aprovechar la caché de capas Docker.
# Si el código cambia pero requirements.txt no, esta capa NO se reconstruye.
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ── ETAPA 4: código de la aplicación ─────────────────────────────
FROM python-deps AS app

WORKDIR /app

# Copiar el código fuente
COPY . .

# Dar permisos de ejecución al entrypoint
RUN chmod +x docker-entrypoint.sh

# Puerto que expone el contenedor (Gunicorn escucha en 8000)
EXPOSE 8000

# Punto de entrada: siempre ejecuta el entrypoint al arrancar
ENTRYPOINT ["./docker-entrypoint.sh"]