from functools import lru_cache

from fastapi import Depends

from app.application.use_cases.process_audio_use_case import ProcessAudioUseCase
from app.domain.interfaces.summarization_service import ISummarizationService
from app.domain.interfaces.transcription_service import ITranscriptionService
from app.infrastructure.ai.flan_t5_service import FlanT5SummarizationService
from app.infrastructure.ai.whisper_service import WhisperTranscriptionService


@lru_cache(maxsize=1)
def get_transcription_service() -> ITranscriptionService:
    """Singleton: Whisper model is loaded only once for the lifetime of the process."""
    return WhisperTranscriptionService()


@lru_cache(maxsize=1)
def get_summarization_service() -> ISummarizationService:
    """Singleton: Flan-T5 model is loaded only once for the lifetime of the process."""
    return FlanT5SummarizationService()


def get_process_audio_use_case(
    transcription_service: ITranscriptionService = Depends(get_transcription_service),
    summarization_service: ISummarizationService = Depends(get_summarization_service),
) -> ProcessAudioUseCase:
    return ProcessAudioUseCase(transcription_service, summarization_service)
