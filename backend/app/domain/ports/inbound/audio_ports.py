from abc import ABC, abstractmethod
from app.domain.entities.audio_analysis import ReportData

class IAnalyzeAudioUseCase(ABC):
    @abstractmethod
    def execute(self, file_path: str, file_name: str, language: str) -> dict:
        ...

class IExportPDFUseCase(ABC):
    @abstractmethod
    def execute(self, data: ReportData) -> bytes:
        ...
