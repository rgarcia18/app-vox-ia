"""
VoxIA Domain Entities — Pipeline Metrics

Entidad que representa las métricas de una ejecución del pipeline.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class PipelineMetrics:
    """Métricas de una ejecución completa del pipeline de análisis."""
    file_name: str
    language: str
    duration_seconds: float
    transcription_time: float
    analysis_time: float
    total_time: float
    transcript_length: int
    summary_length: int
    num_key_points: int
    num_tasks: int
    num_decisions: int
    whisper_model: str
    flan_model: str
    via_grpc: bool = False
    error: Optional[str] = None
