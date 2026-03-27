from dataclasses import dataclass


@dataclass
class AudioFile:
    """Represents an audio file received for processing."""

    filename: str
    content: bytes
    content_type: str


@dataclass
class Transcription:
    """Represents the text transcription of an audio file."""

    text: str


@dataclass
class MeetingAnalysis:
    """Represents the full analysis result of a meeting audio."""

    transcription: str
    summary: str
