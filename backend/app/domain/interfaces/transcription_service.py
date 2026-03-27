from abc import ABC, abstractmethod

from app.domain.entities.meeting import AudioFile, Transcription


class ITranscriptionService(ABC):
    """Contract for any audio transcription implementation."""

    @abstractmethod
    def transcribe(self, audio_file: AudioFile) -> Transcription:
        """Transcribe audio content to text."""
        ...
