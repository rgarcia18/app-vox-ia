"""
VoxIA Whisper Adapter — Transcripción de audio con OpenAI Whisper
"""
import time
from app.domain.entities.audio_analysis import Transcript
from app.domain.ports.outbound.providers.transcription_provider import ITranscriptionProvider
from app.infrastructure.config.settings import settings

_whisper_model = None


def _load_whisper():
    global _whisper_model
    if _whisper_model is None:
        print("⏳ Cargando Whisper...")
        import whisper
        _whisper_model = whisper.load_model(settings.WHISPER_MODEL)
        print(f"✅ Whisper '{settings.WHISPER_MODEL}' listo")
    return _whisper_model


class WhisperAdapter(ITranscriptionProvider):
    def transcribe(self, file_path: str, language: str) -> Transcript:
        model = _load_whisper()
        lang_map = {"es": "spanish", "en": "english"}
        whisper_lang = lang_map.get(language, "spanish")

        start = time.time()
        result = model.transcribe(
            file_path,
            language=whisper_lang,
            verbose=False,
            fp16=False,
            condition_on_previous_text=True,
            compression_ratio_threshold=2.4,
            no_speech_threshold=0.6,
        )
        elapsed = round(time.time() - start, 2)
        segments = result.get("segments", [])
        duration = segments[-1]["end"] if segments else 0

        detected = result.get("language", language)
        lang = (
            "es" if detected in ("es", "spanish")
            else "en" if detected in ("en", "english")
            else language
        )

        return Transcript(
            text=result["text"].strip(),
            language=lang,
            duration_seconds=round(duration, 1),
            processing_time_seconds=elapsed,
        )
