import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from io import BytesIO

from app.core.config import settings
from app.services.ai_service import process_audio_file
from app.services.pdf_service import generate_pdf_report

router = APIRouter(prefix="/api/audio", tags=["audio"])

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".ogg", ".flac", ".webm"}
MAX_SIZE_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


def _cleanup(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


@router.post("/upload")
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = Form(default="es"),
):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail={
            "error": "invalid_format",
            "message": f"Formato no soportado. Usa: {', '.join(ALLOWED_EXTENSIONS)}",
        })

    if language not in ("es", "en"):
        language = "es"

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    temp_path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4()}{ext}")

    try:
        content = await file.read()
        if len(content) > MAX_SIZE_BYTES:
            raise HTTPException(status_code=413, detail={
                "error": "file_too_large",
                "message": f"El archivo supera {settings.MAX_FILE_SIZE_MB}MB",
            })

        with open(temp_path, "wb") as f:
            f.write(content)

        result = process_audio_file(temp_path, language)
        background_tasks.add_task(_cleanup, temp_path)

        return {
            "status": "success",
            "file_name": file.filename,
            "language": result["language"],
            "duration_seconds": result["duration_seconds"],
            "processing_time_seconds": result["processing_time_seconds"],
            "transcript": result["transcript"],
            "summary": result["summary"],
            "key_points": result["key_points"],
            "tasks": result["tasks"],
            "decisions": result["decisions"],
        }

    except HTTPException:
        _cleanup(temp_path)
        raise
    except Exception as e:
        _cleanup(temp_path)
        print(f"Error procesando audio: {e}")
        raise HTTPException(status_code=500, detail={
            "error": "processing_error",
            "message": "Error al procesar el audio. Intenta con otro archivo.",
        })


# ─── Modelo para exportar PDF ─────────────────────────────────────────────────
class ExportPdfRequest(BaseModel):
    file_name: Optional[str] = "grabacion"
    language: Optional[str] = "es"
    duration_seconds: Optional[float] = 0
    processing_time_seconds: Optional[float] = 0
    transcript: Optional[str] = ""
    summary: Optional[str] = ""
    key_points: Optional[list[str]] = []
    tasks: Optional[list[str]] = []
    decisions: Optional[list[str]] = []


@router.post("/export-pdf")
async def export_pdf(body: ExportPdfRequest):
    try:
        pdf_bytes = generate_pdf_report(
            file_name=body.file_name or "grabacion",
            language=body.language or "es",
            duration_seconds=body.duration_seconds or 0,
            processing_time_seconds=body.processing_time_seconds or 0,
            transcript=body.transcript or "",
            summary=body.summary or "",
            key_points=body.key_points or [],
            tasks=body.tasks or [],
            decisions=body.decisions or [],
        )
        safe_name = (body.file_name or "voxia_reporte").replace(" ", "_")
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}_reporte.pdf"'},
        )
    except Exception as e:
        print(f"Error generando PDF: {e}")
        raise HTTPException(status_code=500, detail={
            "error": "pdf_error",
            "message": "Error al generar el PDF.",
        })


@router.get("/health")
async def health():
    return {"status": "ok"}
