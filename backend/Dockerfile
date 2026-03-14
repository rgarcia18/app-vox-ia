# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY pyproject.toml .

# Instalar pip actualizado y dependencias
RUN pip install --upgrade pip && \
    pip install --prefix=/install \
    fastapi \
    uvicorn[standard] \
    python-multipart \
    python-jose[cryptography] \
    passlib[bcrypt] \
    python-dotenv \
    pydantic \
    pydantic-settings \
    transformers \
    torch \
    torchaudio \
    openai-whisper \
    sentencepiece \
    accelerate \
    numpy \
    soundfile \
    aiofiles \
    reportlab \
    "bcrypt==4.0.1" \
    mlflow \
    grpcio \
    grpcio-tools \
    pytest \
    pytest-asyncio \
    httpx

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Instalar ffmpeg en runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias instaladas
COPY --from=builder /install /usr/local

# Copiar código fuente
COPY app/ ./app/
COPY run.py .
COPY grpc_server.py .
COPY tests/ ./tests/

# Crear directorios necesarios
RUN mkdir -p uploads temp

# Exponer puerto
EXPOSE 8000

# Variables de entorno por defecto
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    WHISPER_MODEL=base \
    FLAN_T5_MODEL=google/flan-t5-base \
    FRONTEND_URL=http://localhost:3000 \
    MAX_FILE_SIZE_MB=100

# Comando de inicio
CMD ["python", "run.py"]