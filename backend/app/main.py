from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import get_summarization_service, get_transcription_service
from app.api.v1.audio_router import router as audio_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Load AI models eagerly at startup so the first request is not delayed
    by model download/initialization.
    """
    get_transcription_service()   # warms up Whisper
    get_summarization_service()   # warms up Flan-T5
    yield


app = FastAPI(
    title="VoxIA API",
    description="Audio transcription and meeting summarization powered by Whisper and Flan-T5.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audio_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
