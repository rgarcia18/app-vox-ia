from abc import ABC, abstractmethod
from app.domain.entities.pipeline_metrics import PipelineMetrics

class IMetricsProvider(ABC):
    @abstractmethod
    def log_run(self, metrics: PipelineMetrics) -> None:
        ...

    @abstractmethod
    def log_error(self, file_name: str, language: str, error_message: str) -> None:
        ...
