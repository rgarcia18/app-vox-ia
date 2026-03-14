# VoxIA Backend

Backend de VoxIA — FastAPI + Whisper (ASR) + FLAN-T5 (NLP)

## Pipeline de IA

```
Audio → Whisper → Transcripción → FLAN-T5 → Resumen + Tareas
```

## Requisitos previos

### 1. Instalar uv

Abre PowerShell y ejecuta:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Cierra y vuelve a abrir la terminal. Verifica:

```bash
uv --version
```

### 2. Instalar FFmpeg

1. Descargar desde https://ffmpeg.org/download.html → Windows builds → **ffmpeg-release-essentials.zip**
2. Extraer en `C:\ffmpeg`
3. Agregar `C:\ffmpeg\bin` al PATH de Windows:
   - Busca "Variables de entorno" en el menú inicio
   - "Variables del sistema" → `Path` → Editar → Nuevo → escribe `C:\ffmpeg\bin`
4. Verifica en terminal nueva: `ffmpeg -version`

---

## Instalación y ejecución

```bash
# Entrar a la carpeta backend
cd C:\Users\user\Desktop\app-vox-ia\backend

# Instalar dependencias (uv crea el entorno automáticamente)
uv sync

# Correr el servidor
uv run python run.py
```

El servidor arranca en **http://localhost:8000**

Documentación interactiva: **http://localhost:8000/docs**

> ⚠️ La primera vez que subas un audio, Whisper y FLAN-T5 se descargan de
> HuggingFace (~1.5 GB). Necesitas conexión a internet.

---

## Credenciales por defecto

```
Usuario:    admin
Contraseña: password123
```

Configurable en `.env`.

---

## Conectar con el frontend

**1.** Reemplaza `frontend/services/authService.ts` con el `authService.ts` incluido en este zip.

**2.** Crea `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**3.** Corre ambos en terminales separadas:

```bash
# Terminal 1 — Backend
cd app-vox-ia/backend
uv run python run.py

# Terminal 2 — Frontend
cd app-vox-ia/frontend
npx next dev
```

---

## Estructura

```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── core/
│   │   ├── config.py        # Variables de entorno
│   │   └── security.py      # JWT + bcrypt
│   ├── models/
│   │   └── user.py          # Usuarios en memoria
│   ├── routers/
│   │   ├── auth.py          # Login / Refresh / Logout
│   │   └── audio.py         # Upload + procesamiento
│   └── services/
│       └── ai_service.py    # Whisper + FLAN-T5
├── .env                     # Configuración local
├── pyproject.toml           # Dependencias (uv)
└── run.py                   # Punto de entrada
```

## Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/refresh` | Renovar token |
| POST | `/api/auth/logout` | Cerrar sesión |
| POST | `/api/audio/upload` | Procesar audio |
| GET  | `/api/audio/health` | Estado del servicio |
