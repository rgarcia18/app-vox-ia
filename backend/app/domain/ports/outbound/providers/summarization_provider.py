from abc import ABC, abstractmethod
from app.domain.entities.audio_analysis import AnalysisResult

class ISummarizationProvider(ABC):
    @abstractmethod
    def analyze(self, text: str, language: str) -> AnalysisResult:
        ...
