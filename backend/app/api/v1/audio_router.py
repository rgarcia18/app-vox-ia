import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.dependencies import get_process_audio_use_case
from app.api.v1.schemas import MeetingAnalysisResponse
from app.application.use_cases.process_audio_use_case import ProcessAudioUseCase
from app.domain.entities.meeting import AudioFile

router = APIRouter(prefix="/audio", tags=["Audio Processing"])

_ALLOWED_CONTENT_TYPES = {"audio/mpeg", "audio/mp3", "audio/x-mpeg", "audio/x-mp3"}
_MAX_FILE_SIZE_MB = 25
_MAX_FILE_SIZE_BYTES = _MAX_FILE_SIZE_MB * 1024 * 1024


@router.post(
    "/process",
    response_model=MeetingAnalysisResponse,
    summary="Transcribe and summarize a meeting audio file",
    description=(
        "Receives an MP3 audio file, transcribes it using OpenAI Whisper (base), "
        "and generates a meeting summary with key tasks using Google Flan-T5 (base)."
    ),
    status_code=status.HTTP_200_OK,
)
async def process_audio(
    file: UploadFile = File(..., description="MP3 audio file of the meeting"),
    use_case: ProcessAudioUseCase = Depends(get_process_audio_use_case),
) -> MeetingAnalysisResponse:
    _validate_content_type(file)

    content = await file.read()
    _validate_file_size(content)

    audio_file = AudioFile(
        filename=file.filename or "audio.mp3",
        content=content,
        content_type=file.content_type or "audio/mpeg",
    )

    # Run CPU-bound inference in a thread pool to avoid blocking the event loop
    analysis = await asyncio.to_thread(use_case.execute, audio_file)

    return MeetingAnalysisResponse(
        transcription=analysis.transcription,
        summary=analysis.summary,
    )


def _validate_content_type(file: UploadFile) -> None:
    content_type = (file.content_type or "").lower()
    filename = (file.filename or "").lower()

    if content_type not in _ALLOWED_CONTENT_TYPES and not filename.endswith((".mp3", ".mpeg")):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported file type '{file.content_type}'. "
                "Only MP3 audio files are accepted."
            ),
        )


def _validate_file_size(content: bytes) -> None:
    if len(content) > _MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the {_MAX_FILE_SIZE_MB} MB limit.",
        )
