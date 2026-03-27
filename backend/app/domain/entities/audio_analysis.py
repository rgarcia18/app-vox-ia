"""
VoxIA Domain Entities — Audio Analysis

Entidades del dominio: objetos de valor puros sin dependencias externas.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Transcript:
    """Resultado de la transcripción de un audio."""
    text: str
    language: str
    duration_seconds: float
    processing_time_seconds: float


@dataclass
class AnalysisResult:
    """Resultado del análisis NLP de un transcript."""
    summary: str
    key_points: list[str]
    tasks: list[str]
    decisions: list[str]
    via_grpc: bool = False


@dataclass
class ReportData:
    """Datos requeridos para generar un reporte PDF."""
    file_name: str
    language: str
    duration_seconds: float
    processing_time_seconds: float
    transcript: str
    summary: str
    key_points: list[str]
    tasks: list[str]
    decisions: list[str]
