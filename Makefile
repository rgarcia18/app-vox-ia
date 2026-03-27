.PHONY: help backend backend-debug frontend install install-backend install-frontend test test-backend lint-frontend dev

# Limpia VIRTUAL_ENV para evitar conflictos con otros proyectos
unexport VIRTUAL_ENV

help:
	@echo "Comandos disponibles:"
	@echo "  make install          - Instala dependencias de backend y frontend"
	@echo "  make install-backend  - Instala dependencias del backend (uv)"
	@echo "  make install-frontend - Instala dependencias del frontend (npm)"
	@echo "  make backend          - Inicia el backend en localhost:8000"
	@echo "  make backend-debug    - Inicia el backend con logs detallados (debug)"
	@echo "  make frontend         - Inicia el frontend en localhost:3000"
	@echo "  make dev              - Inicia backend y frontend en paralelo"
	@echo "  make test             - Ejecuta tests del backend"
	@echo "  make lint-frontend    - Ejecuta el linter del frontend"
	@echo "  make docker-up        - Levanta todo con Docker Compose"
	@echo "  make docker-down      - Detiene los contenedores de Docker Compose"

# ── Instalación ──────────────────────────────────────────────────────────────

install: install-backend install-frontend

install-backend:
	cd backend && uv sync

# Instala las dependencias de ML (torch, whisper, transformers) usando el índice
# CPU de PyTorch. Necesario porque torch no tiene wheel oficial para macOS Intel
# en PyPI. Ejecutar sólo si quieres correr los modelos localmente.
install-ml:
	brew install ffmpeg
	cd backend && uv pip install --only-binary llvmlite --only-binary numba ".[ml]"

install-frontend:
	cd frontend && npm install

# ── Desarrollo local ─────────────────────────────────────────────────────────

backend:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

backend-debug:
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

frontend:
	cd frontend && npm run dev

dev:
	@echo "Iniciando backend y frontend en paralelo..."
	@$(MAKE) backend & $(MAKE) frontend

# ── Tests y linting ──────────────────────────────────────────────────────────

test-backend:
	cd backend && uv run pytest

test: test-backend

lint-frontend:
	cd frontend && npm run lint

# ── Docker ───────────────────────────────────────────────────────────────────

docker-up:
	docker compose up --build

docker-down:
	docker compose down