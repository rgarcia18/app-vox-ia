FROM python:3.11-slim

# Dependencias del sistema (ffmpeg para whisper)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar uv y setuptools (requerido por openai-whisper)
RUN pip install --no-cache-dir uv setuptools

# Copiar definición de dependencias e instalar
# Se usa el índice CPU de PyTorch para evitar descargar librerías CUDA (~7GB → ~2GB)
COPY pyproject.toml .
RUN uv pip install --system --no-cache --no-build-isolation \
    --index-url https://download.pytorch.org/whl/cpu \
    --extra-index-url https://pypi.org/simple \
    -r pyproject.toml \
    ".[ml]"

# Copiar el código fuente
COPY . .

# Regenerar stubs gRPC con la versión de protobuf instalada (evita incompatibilidad de versiones)
RUN uv pip install --system --no-cache grpcio-tools && python generate_grpc.py

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
