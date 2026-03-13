from app.domain.entities.meeting import AudioFile, MeetingAnalysis
from app.domain.interfaces.summarization_service import ISummarizationService
from app.domain.interfaces.transcription_service import ITranscriptionService


class ProcessAudioUseCase:
    """
    Orchestrates the full audio processing pipeline:
    1. Transcribes the audio using a speech-to-text model.
    2. Generates a meeting summary with key tasks using a language model.
    """

    def __init__(
        self,
        transcription_service: ITranscriptionService,
        summarization_service: ISummarizationService,
    ) -> None:
        self._transcription_service = transcription_service
        self._summarization_service = summarization_service

    def execute(self, audio_file: AudioFile) -> MeetingAnalysis:
        transcription = self._transcription_service.transcribe(audio_file)
        analysis = self._summarization_service.summarize(transcription)
        return analysis
