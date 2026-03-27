import time
from app.domain.ports.inbound.audio_ports import IAnalyzeAudioUseCase
from app.domain.entities.pipeline_metrics import PipelineMetrics
from app.domain.ports.outbound.providers.transcription_provider import ITranscriptionProvider
from app.domain.ports.outbound.providers.summarization_provider import ISummarizationProvider
from app.domain.ports.outbound.providers.metrics_provider import IMetricsProvider

class AnalyzeAudioUseCase(IAnalyzeAudioUseCase):
    def __init__(
        self,
        transcriber: ITranscriptionProvider,
        analyzer: ISummarizationProvider,
        tracker: IMetricsProvider,
        whisper_model: str,
        flan_model: str,
    ):
        self._transcriber = transcriber
        self._analyzer = analyzer
        self._tracker = tracker
        self._whisper_model = whisper_model
        self._flan_model = flan_model

    def execute(self, file_path: str, file_name: str, language: str) -> dict:
        total_start = time.time()

        print("🎙️  [1/2] Transcribiendo audio...")
        t0 = time.time()
        transcript = self._transcriber.transcribe(file_path, language)
        transcription_time = round(time.time() - t0, 2)

        if not transcript.text or len(transcript.text.strip()) < 10:
            total_time = round(time.time() - total_start, 2)
            self._tracker.log_run(PipelineMetrics(
                file_name=file_name,
                language=transcript.language,
                duration_seconds=transcript.duration_seconds,
                transcription_time=transcription_time,
                analysis_time=0,
                total_time=total_time,
                transcript_length=0,
                summary_length=0,
                num_key_points=0,
                num_tasks=0,
                num_decisions=0,
                whisper_model=self._whisper_model,
                flan_model=self._flan_model,
            ))
            return {
                "status": "success",
                "file_name": file_name,
                "language": transcript.language,
                "duration_seconds": transcript.duration_seconds,
                "processing_time_seconds": total_time,
                "transcript": "",
                "summary": "No se detectó voz en el audio.",
                "key_points": [],
                "tasks": [],
                "decisions": [],
            }

        print("📝  [2/2] Analizando texto vía gRPC...")
        t1 = time.time()
        analysis = self._analyzer.analyze(transcript.text, transcript.language)
        analysis_time = round(time.time() - t1, 2)
        total_time = round(time.time() - total_start, 2)

        self._tracker.log_run(PipelineMetrics(
            file_name=file_name,
            language=transcript.language,
            duration_seconds=transcript.duration_seconds,
            transcription_time=transcription_time,
            analysis_time=analysis_time,
            total_time=total_time,
            transcript_length=len(transcript.text),
            summary_length=len(analysis.summary),
            num_key_points=len(analysis.key_points),
            num_tasks=len(analysis.tasks),
            num_decisions=len(analysis.decisions),
            whisper_model=self._whisper_model,
            flan_model=self._flan_model,
            via_grpc=analysis.via_grpc,
        ))

        print(f"🏁  Pipeline listo en {total_time}s | gRPC={analysis.via_grpc}")

        return {
            "status": "success",
            "file_name": file_name,
            "language": transcript.language,
            "duration_seconds": transcript.duration_seconds,
            "processing_time_seconds": total_time,
            "transcript": transcript.text,
            "summary": analysis.summary,
            "key_points": analysis.key_points,
            "tasks": analysis.tasks,
            "decisions": analysis.decisions,
        }
