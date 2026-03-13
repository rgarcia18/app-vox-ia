from pydantic import BaseModel


class MeetingAnalysisResponse(BaseModel):
    """API response returned after processing a meeting audio file."""

    transcription: str
    summary: str

    model_config = {"from_attributes": True}
