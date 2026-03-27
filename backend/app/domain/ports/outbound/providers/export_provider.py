from abc import ABC, abstractmethod
from app.domain.entities.audio_analysis import ReportData

class IExportProvider(ABC):
    @abstractmethod
    def generate(self, data: ReportData) -> bytes:
        ...
