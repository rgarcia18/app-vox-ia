from abc import ABC, abstractmethod

from app.domain.entities.meeting import MeetingAnalysis, Transcription


class ISummarizationService(ABC):
    """Contract for any meeting summarization implementation."""

    @abstractmethod
    def summarize(self, transcription: Transcription) -> MeetingAnalysis:
        """Generate a meeting summary and extract key tasks from a transcription."""
        ...
