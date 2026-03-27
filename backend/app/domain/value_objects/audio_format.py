from enum import Enum

class AudioFormat(str, Enum):
    MP3 = ".mp3"
    WAV = ".wav"
    M4A = ".m4a"
    MP4 = ".mp4"
    OGG = ".ogg"
    FLAC = ".flac"
    WEBM = ".webm"
