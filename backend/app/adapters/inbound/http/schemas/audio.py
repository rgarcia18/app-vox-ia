from pydantic import BaseModel
from typing import Optional

class ExportPdfRequest(BaseModel):
    file_name: Optional[str] = "grabacion"
    language: Optional[str] = "es"
    duration_seconds: Optional[float] = 0
    processing_time_seconds: Optional[float] = 0
    transcript: Optional[str] = ""
    summary: Optional[str] = ""
    key_points: Optional[list[str]] = []
    tasks: Optional[list[str]] = []
    decisions: Optional[list[str]] = []
