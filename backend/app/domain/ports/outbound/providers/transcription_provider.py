from abc import ABC, abstractmethod
from app.domain.entities.audio_analysis import Transcript

class ITranscriptionProvider(ABC):
    @abstractmethod
    def transcribe(self, file_path: str, language: str) -> Transcript:
        ...
