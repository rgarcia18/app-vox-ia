import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from io import BytesIO

from app.infrastructure.config.settings import settings
from app.domain.entities.audio_analysis import ReportData
from app.domain.ports.inbound.audio_ports import IAnalyzeAudioUseCase, IExportPDFUseCase
from app.domain.ports.outbound.providers.metrics_provider import IMetricsProvider
from app.domain.ports.outbound.providers.health_provider import IHealthProvider
from app.adapters.inbound.http.schemas.audio import ExportPdfRequest
from app.infrastructure.container.dependencies import (
    get_analyze_audio_use_case,
    get_export_pdf_use_case,
    get_metrics_provider,
    get_health_provider,
)

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
    use_case: IAnalyzeAudioUseCase = Depends(get_analyze_audio_use_case),
    tracker: IMetricsProvider = Depends(get_metrics_provider),
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

        background_tasks.add_task(_cleanup, temp_path)

        return use_case.execute(
            file_path=temp_path,
            file_name=file.filename or "unknown",
            language=language,
        )

    except HTTPException:
        _cleanup(temp_path)
        raise
    except Exception as e:
        _cleanup(temp_path)
        print(f"❌ Error procesando audio: {e}")
        tracker.log_error(
            file_name=file.filename or "unknown",
            language=language,
            error_message=str(e),
        )
        raise HTTPException(status_code=500, detail={
            "error": "processing_error",
            "message": "Error al procesar el audio. Intenta con otro archivo.",
        })


@router.post("/export-pdf")
async def export_pdf(
    body: ExportPdfRequest,
    use_case: IExportPDFUseCase = Depends(get_export_pdf_use_case),
):
    try:
        data = ReportData(
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
        pdf_bytes = use_case.execute(data)
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
async def health(checker: IHealthProvider = Depends(get_health_provider)):
    grpc_ok = checker.is_healthy()
    return {
        "status": "ok",
        "grpc_server": "online" if grpc_ok else "offline (usando fallback)",
    }
