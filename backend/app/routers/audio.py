import os
import time
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from io import BytesIO

from app.core.config import settings
from app.services.ai_service import transcribe_audio
from app.services.pdf_service import generate_pdf_report
from app.services.mlflow_tracker import log_pipeline_run, log_error_run

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
    total_start = time.time()

    try:
        content = await file.read()
        if len(content) > MAX_SIZE_BYTES:
            raise HTTPException(status_code=413, detail={
                "error": "file_too_large",
                "message": f"El archivo supera {settings.MAX_FILE_SIZE_MB}MB",
            })

        with open(temp_path, "wb") as f:
            f.write(content)

        # ── 1. Transcripción con Whisper ───────────────────────────────────────
        print("🎙️  [1/2] Transcribiendo audio...")
        t0 = time.time()
        transcription = transcribe_audio(temp_path, language)
        transcription_time = round(time.time() - t0, 2)

        transcript = transcription["text"]
        detected_lang = transcription.get("language", language)
        lang = "es" if detected_lang in ("es", "spanish") else "en" if detected_lang in ("en", "english") else language

        background_tasks.add_task(_cleanup, temp_path)

        if not transcript or len(transcript.strip()) < 10:
            total_time = round(time.time() - total_start, 2)
            log_pipeline_run(
                file_name=file.filename or "unknown",
                language=lang,
                duration_seconds=transcription.get("duration_seconds", 0),
                transcription_time=transcription_time,
                analysis_time=0,
                total_time=total_time,
                transcript_length=0,
                summary_length=0,
                num_key_points=0,
                num_tasks=0,
                num_decisions=0,
                whisper_model=settings.WHISPER_MODEL,
                flan_model=settings.FLAN_T5_MODEL,
                via_grpc=False,
            )
            return {
                "status": "success",
                "file_name": file.filename,
                "language": lang,
                "duration_seconds": transcription.get("duration_seconds", 0),
                "processing_time_seconds": total_time,
                "transcript": "",
                "summary": "No se detectó voz en el audio.",
                "key_points": [],
                "tasks": [],
                "decisions": [],
            }

        # ── 2. Análisis NLP vía gRPC (con fallback directo) ───────────────────
        print("📝  [2/2] Analizando texto vía gRPC...")
        t1 = time.time()
        # Lazy import to avoid module-level import errors
        try:
            from app.grpc_service.grpc_client import analyze_text_via_grpc
        except (ImportError, ModuleNotFoundError):
            # If gRPC fails, use fallback directly
            from app.services.ai_service import (
                generate_summary,
                extract_key_points,
                extract_tasks,
                extract_decisions,
            )
            analysis = {
                "summary": generate_summary(transcript, lang),
                "key_points": extract_key_points(transcript, lang),
                "tasks": extract_tasks(transcript, lang),
                "decisions": extract_decisions(transcript, lang),
                "via_grpc": False,
            }
        else:
            analysis = analyze_text_via_grpc(transcript, lang)
        analysis_time = round(time.time() - t1, 2)

        total_time = round(time.time() - total_start, 2)

        # ── 3. Registrar en MLflow ─────────────────────────────────────────────
        log_pipeline_run(
            file_name=file.filename or "unknown",
            language=lang,
            duration_seconds=transcription.get("duration_seconds", 0),
            transcription_time=transcription_time,
            analysis_time=analysis_time,
            total_time=total_time,
            transcript_length=len(transcript),
            summary_length=len(analysis.get("summary", "")),
            num_key_points=len(analysis.get("key_points", [])),
            num_tasks=len(analysis.get("tasks", [])),
            num_decisions=len(analysis.get("decisions", [])),
            whisper_model=settings.WHISPER_MODEL,
            flan_model=settings.FLAN_T5_MODEL,
            via_grpc=analysis.get("via_grpc", False),
        )

        print(f"🏁  Pipeline listo en {total_time}s | gRPC={analysis.get('via_grpc')}")

        return {
            "status": "success",
            "file_name": file.filename,
            "language": lang,
            "duration_seconds": transcription.get("duration_seconds", 0),
            "processing_time_seconds": total_time,
            "transcript": transcript,
            "summary": analysis.get("summary", ""),
            "key_points": analysis.get("key_points", []),
            "tasks": analysis.get("tasks", []),
            "decisions": analysis.get("decisions", []),
        }

    except HTTPException:
        _cleanup(temp_path)
        raise
    except Exception as e:
        _cleanup(temp_path)
        print(f"❌ Error procesando audio: {e}")
        log_error_run(
            file_name=file.filename or "unknown",
            language=language,
            error_message=str(e),
        )
        raise HTTPException(status_code=500, detail={
            "error": "processing_error",
            "message": "Error al procesar el audio. Intenta con otro archivo.",
        })


# ─── Exportar PDF ──────────────────────────────────────────────────────────────
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
        print(f"❌ Error generando PDF: {e}")
        raise HTTPException(status_code=500, detail={
            "error": "pdf_error",
            "message": "Error al generar el PDF.",
        })


@router.get("/health")
async def health():
    from app.grpc_service.grpc_client import health_check_grpc
    grpc_ok = health_check_grpc()
    return {
        "status": "ok",
        "grpc_server": "online" if grpc_ok else "offline (usando fallback)",
    }
