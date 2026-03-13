import os
import tempfile
import warnings

import numpy as np
import torchaudio
from transformers import pipeline

from app.domain.entities.meeting import AudioFile, Transcription
from app.domain.interfaces.transcription_service import ITranscriptionService

_WHISPER_MODEL = "openai/whisper-base"
_TARGET_SAMPLE_RATE = 16_000  # Whisper requires 16 kHz mono PCM


class WhisperTranscriptionService(ITranscriptionService):
    """
    Transcription service backed by OpenAI Whisper (base) via HuggingFace Transformers.

    Audio decoding is handled by torchaudio (bundled FFmpeg), which supports
    MP3 without requiring a system-level ffmpeg installation.

    The ASR pipeline is loaded once at instantiation and reused across all
    requests to avoid repeated model weight initialisation overhead.
    """

    def __init__(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self._pipeline = pipeline(
                task="automatic-speech-recognition",
                model=_WHISPER_MODEL,
                chunk_length_s=30,  # sliding-window chunking for long-form audio
            )

    def transcribe(self, audio_file: AudioFile) -> Transcription:
        """
        1. Writes raw audio bytes to a temporary file.
        2. Decodes and resamples to 16 kHz mono via torchaudio.
        3. Runs Whisper inference on the resulting numpy array.
        4. Returns a Transcription entity.
        """
        suffix = self._resolve_suffix(audio_file.content_type, audio_file.filename)

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_file.content)
            tmp_path = tmp.name

        try:
            audio_array = self._load_audio(tmp_path)
        finally:
            os.unlink(tmp_path)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = self._pipeline(
                {"array": audio_array, "sampling_rate": _TARGET_SAMPLE_RATE},
                return_timestamps=False,
                generate_kwargs={"language": None, "task": "transcribe"},
            )
        text: str = result["text"].strip()  # type: ignore[index]
        return Transcription(text=text)

    @staticmethod
    def _load_audio(path: str) -> np.ndarray:
        """Decode audio, resample to 16 kHz and convert to mono float32."""
        waveform, sample_rate = torchaudio.load(path)

        if sample_rate != _TARGET_SAMPLE_RATE:
            resampler = torchaudio.transforms.Resample(
                orig_freq=sample_rate,
                new_freq=_TARGET_SAMPLE_RATE,
            )
            waveform = resampler(waveform)

        # Average channels to mono
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)

        return waveform.squeeze().numpy().astype(np.float32)

    @staticmethod
    def _resolve_suffix(content_type: str, filename: str) -> str:
        if "mp3" in content_type or filename.lower().endswith(".mp3"):
            return ".mp3"
        if "wav" in content_type or filename.lower().endswith(".wav"):
            return ".wav"
        return ".mp3"
