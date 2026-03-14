# 🎙️ VoxIA — Transcripción Inteligente de Reuniones

> Sistema de procesamiento de audio con Inteligencia Artificial que convierte reuniones y clases en documentos estructurados con transcripción, resumen ejecutivo, puntos clave, tareas y decisiones.

**Universidad Autónoma de Occidente — Especialización en Inteligencia Artificial**  
**Profesor:** Jan Polanco Velasco

---

## 👥 Autores

| Nombre | Código | GitHub |
|--------|--------|--------|
| Santiago Londoño Méndez | 22602902 | [@SANTIAGOlmF14](https://github.com/SANTIAGOlmF14) |
| Andrés Rojas Zúñiga | 22507348 | [@androjzu7-stack](https://github.com/androjzu7-stack) |
| Rubén Darío García Morales | 22507004 | [@rgarcia18](https://github.com/rgarcia18) |
| David Ayala Caro | 22507570 | [@davidr-ac](https://github.com/davidr-ac) |

---

## 🧠 ¿Qué hace VoxIA?

VoxIA automatiza la documentación de reuniones y clases mediante un pipeline de IA de extremo a extremo:

```
Audio (.mp3 / .wav / .m4a)
        ↓
  Whisper Base (ASR)
        ↓
   Transcripción
        ↓
  FLAN-T5 Base (NLP)  ←→  gRPC Server (puerto 50051)
        ↓
  ┌─────────────────────────────┐
  │  Resumen Ejecutivo          │
  │  Puntos Clave               │
  │  Tareas y Compromisos       │
  │  Decisiones Tomadas         │
  └─────────────────────────────┘
        ↓
   Reporte PDF
        ↓
   MLflow Tracking (métricas)
```

---

## 🏗️ Arquitectura del Sistema

```
app-vox-ia/
├── backend/                        # FastAPI + Python
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py           # Variables de entorno
│   │   │   └── security.py         # JWT + bcrypt
│   │   ├── grpc_service/
│   │   │   ├── voxia.proto         # Definición del servicio gRPC
│   │   │   ├── voxia_pb2.py        # Stubs generados (proto)
│   │   │   ├── voxia_pb2_grpc.py   # Stubs generados (grpc)
│   │   │   └── grpc_client.py      # Cliente gRPC con fallback
│   │   ├── models/
│   │   │   └── user.py             # Usuarios en memoria
│   │   ├── routers/
│   │   │   ├── auth.py             # Login / Refresh / Logout
│   │   │   └── audio.py            # Upload + exportación PDF
│   │   └── services/
│   │       ├── ai_service.py       # Whisper + FLAN-T5
│   │       ├── pdf_service.py      # Generación de reportes PDF
│   │       └── mlflow_tracker.py   # Tracking de experimentos
│   ├── tests/
│   │   ├── conftest.py             # Configuración pytest
│   │   ├── test_ai_service.py      # 27 pruebas del pipeline IA
│   │   ├── test_grpc_client.py     # 8 pruebas del cliente gRPC
│   │   └── test_mlflow_tracker.py  # 5 pruebas del tracker MLflow
│   ├── grpc_server.py              # Servidor gRPC (puerto 50051)
│   ├── generate_grpc.py            # Generador de stubs
│   ├── run.py                      # Punto de entrada FastAPI
│   ├── pyproject.toml              # Dependencias
│   └── .env                        # Variables locales
└── frontend/                       # Next.js 16 + TypeScript
    ├── app/
    │   ├── page.tsx                # Página de login
    │   └── dashboard/
    │       └── page.tsx            # Dashboard principal
    ├── components/
    │   ├── dashboard/
    │   │   ├── FileUpload.tsx      # Carga de archivos de audio
    │   │   ├── LiveRecording.tsx   # Grabación en vivo
    │   │   ├── ModeSelector.tsx    # Selector de modo
    │   │   ├── ResultsPanel.tsx    # Visualización de resultados
    │   │   └── DashboardHeader.tsx # Header con logout
    │   └── shared/
    │       ├── LoginForm.tsx       # Formulario de login
    │       └── AnimatedBackground.tsx
    ├── services/
    │   ├── api.ts                  # Cliente Axios configurado
    │   └── authService.ts          # Servicio de autenticación
    ├── stores/
    │   └── authStore.ts            # Estado global (Zustand)
    ├── next.config.ts              # Proxy al backend
    └── .env.local                  # Variables de entorno
```

---

## 🤖 Modelos de Inteligencia Artificial

### Whisper Base — `openai/whisper-base`
- **Tarea:** Automatic Speech Recognition (ASR)
- **Parámetros:** 74 millones
- **Arquitectura:** Transformer Encoder-Decoder (seq2seq)
- **Idiomas:** ~99 idiomas (español e inglés en VoxIA)
- **Licencia:** Apache 2.0

### FLAN-T5 Base — `google/flan-t5-base`
- **Tarea:** Text-to-Text Generation (resumen, extracción)
- **Parámetros:** 250 millones
- **Arquitectura:** T5 con Instruction Fine-Tuning
- **Paradigma:** Zero-shot learning
- **Licencia:** Apache 2.0

---

## ⚙️ Requisitos del Sistema

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| RAM | 8 GB | 16 GB |
| Almacenamiento | 10 GB libres | 15 GB libres |
| GPU VRAM | — | 6–8 GB (CUDA) |
| Python | 3.9+ | 3.11 |
| Node.js | 18+ | 22+ |

---

## 🚀 Instalación y Ejecución

### Prerrequisitos

**1. Instalar FFmpeg** (necesario para Whisper):
```powershell
winget install ffmpeg
# Luego recargar el PATH:
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

**2. Verificar FFmpeg:**
```powershell
ffmpeg -version
```

---

### Backend

```powershell
cd backend

# Instalar dependencias
python -m pip install setuptools
python -m pip install openai-whisper --no-build-isolation
python -m pip install reportlab fastapi "uvicorn[standard]" python-jose "passlib[bcrypt]" python-multipart python-dotenv transformers torch sentencepiece accelerate pydantic pydantic-settings aiofiles mlflow grpcio grpcio-tools pytest "bcrypt==4.0.1"

# Generar stubs gRPC (solo una vez)
python generate_grpc.py

# Iniciar el servidor FastAPI (Terminal 1)
python run.py
```

El backend queda disponible en **http://localhost:8000**  
Documentación interactiva: **http://localhost:8000/docs**

---

### Frontend

```powershell
cd frontend
npm install
npx next dev
```

El frontend queda disponible en **http://localhost:3000**

---

### Servidor gRPC (opcional, Terminal 3)

```powershell
cd backend
python grpc_server.py
```

El servidor gRPC escucha en el **puerto 50051**. Si no está corriendo, el sistema usa fallback directo automáticamente sin interrupciones.

---

### MLflow UI (opcional, Terminal 4)

```powershell
cd backend
python -m mlflow ui
```

Dashboard de métricas disponible en **http://localhost:5000**

---

## 🔐 Credenciales por Defecto

```
Usuario:    admin
Contraseña: password123
```

Configurable en `backend/.env`.

---

## 📡 API Endpoints

### Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/login` | Iniciar sesión |
| POST | `/api/auth/refresh` | Renovar access token |
| POST | `/api/auth/logout` | Cerrar sesión |

### Audio
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/audio/upload` | Procesar archivo de audio |
| POST | `/api/audio/export-pdf` | Generar reporte PDF |
| GET | `/api/audio/health` | Estado del servicio + gRPC |

---

## 🔗 gRPC — Comunicación entre Servicios

El servicio gRPC expone el análisis NLP de forma independiente al servidor HTTP:

```protobuf
service VoxIAService {
  rpc AnalyzeText (AnalyzeRequest) returns (AnalyzeResponse);
  rpc HealthCheck (HealthRequest)  returns (HealthResponse);
}
```

**Flujo:**
1. FastAPI recibe el audio → Whisper transcribe
2. FastAPI llama al servidor gRPC con el texto transcrito
3. El servidor gRPC ejecuta FLAN-T5 y devuelve resumen, puntos clave, tareas y decisiones
4. Si gRPC no está disponible → fallback directo (sin interrupciones)

**Regenerar stubs** (si se modifica el `.proto`):
```powershell
python generate_grpc.py
```

---

## 📊 MLflow — Tracking de Experimentos

Cada ejecución del pipeline registra automáticamente en MLflow:

**Parámetros:**
- Modelo Whisper y FLAN-T5 usados
- Idioma detectado
- Nombre del archivo
- Si se usó gRPC o fallback

**Métricas:**
- `audio_duration_seconds` — duración del audio
- `transcription_time_s` — tiempo de transcripción
- `analysis_time_s` — tiempo de análisis NLP
- `total_pipeline_time_s` — tiempo total
- `transcript_chars` — longitud de la transcripción
- `summary_chars` — longitud del resumen
- `num_key_points` — puntos clave encontrados
- `num_tasks` — tareas identificadas
- `num_decisions` — decisiones identificadas
- `real_time_factor` — ratio tiempo_proceso / duración_audio

**Ver métricas:**
```powershell
python -m mlflow ui
# → http://localhost:5000
```

---

## 🧪 Pruebas Unitarias

```powershell
cd backend
python -m pytest tests/ -v
```

**Resultado esperado: 40/40 tests passing**

| Módulo | Tests | Descripción |
|--------|-------|-------------|
| `test_ai_service.py` | 27 | Pipeline IA: parse, truncate, resumen, tareas, decisiones |
| `test_grpc_client.py` | 8 | Cliente gRPC: conexión, fallback, health check |
| `test_mlflow_tracker.py` | 5 | Tracker MLflow: registro, errores, métricas |

---

## 🛠️ Stack Tecnológico

### Backend
- **FastAPI** — Framework web asíncrono
- **Whisper** — ASR (OpenAI)
- **FLAN-T5** — NLP (Google / HuggingFace)
- **gRPC** — Comunicación entre servicios
- **MLflow** — Tracking de experimentos
- **ReportLab** — Generación de PDF
- **JWT + bcrypt** — Autenticación segura
- **pytest** — Pruebas unitarias

### Frontend
- **Next.js 16** — Framework React
- **TypeScript** — Tipado estático
- **Tailwind CSS 4** — Estilos
- **Framer Motion** — Animaciones
- **Zustand** — Estado global
- **Axios** — Cliente HTTP
- **Sonner** — Notificaciones

---

## 📋 Funcionalidades

- ✅ Carga de archivos de audio (MP3, WAV, M4A, OGG, FLAC)
- ✅ Grabación de audio en vivo desde el navegador
- ✅ Transcripción automática en español e inglés
- ✅ Resumen ejecutivo abstractivo
- ✅ Extracción de puntos clave
- ✅ Identificación de tareas y compromisos
- ✅ Identificación de decisiones tomadas
- ✅ Exportación de reporte en PDF
- ✅ Comunicación via gRPC con fallback automático
- ✅ Tracking de métricas con MLflow
- ✅ Autenticación con JWT (access + refresh tokens)
- ✅ Interfaz web responsiva con tema oscuro

---

## ⚠️ Limitaciones Conocidas

- El sistema **no es tiempo real** — procesa audio grabado o al finalizar la grabación
- FLAN-T5 base tiene **capacidad limitada en español** — es un modelo pequeño entrenado principalmente en inglés
- El procesamiento en **CPU** puede tardar entre 1–5 minutos según la duración del audio
- No realiza **diarización** (identificación de hablantes)
- No procesa **video** ni contenido multimodal

---

## 📁 Repositorio

**GitHub Projects (Kanban):** https://github.com/users/rgarcia18/projects/1

---

*Generado con VoxIA — Universidad Autónoma de Occidente · 2026*
