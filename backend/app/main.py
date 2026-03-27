"""
VoxIA Backend - FastAPI

Pipeline de IA:
  Audio → Whisper (ASR) → Texto → FLAN-T5 (NLP) → Resumen + Tareas
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.infrastructure.config.settings import settings
from app.adapters.inbound.http.routers import auth, audio
from app.infrastructure.exceptions.handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 VoxIA Backend iniciando...")
    print(f"   Whisper model: {settings.WHISPER_MODEL}")
    print(f"   FLAN-T5 model: {settings.FLAN_T5_MODEL}")
    print(f"   Frontend URL:  {settings.FRONTEND_URL}")
    print("✅ Backend listo en http://localhost:8000")
    print("📖 Documentación: http://localhost:8000/docs")
    yield
    print("🛑 VoxIA Backend apagando...")


app = FastAPI(
    title="VoxIA API",
    description="Backend de transcripción y análisis de reuniones con IA",
    version="1.0.0",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(audio.router)


@app.get("/")
async def root():
    return {
        "app": "VoxIA API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "auth": {
                "login": "POST /api/auth/login",
                "refresh": "POST /api/auth/refresh",
                "logout": "POST /api/auth/logout",
            },
            "audio": {
                "upload": "POST /api/audio/upload",
                "health": "GET /api/audio/health",
            },
        },
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
