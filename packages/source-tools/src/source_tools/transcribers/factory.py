from dataclasses import dataclass

from source_tools.transcribers.audio_pipeline import AudioPipeline
from source_tools.transcribers.base import Transcriber
from source_tools.transcribers.groq import GroqTranscriber
from source_tools.transcribers.nemotron import NemotronTranscriber
from source_tools.transcribers.pipeline import TranscriberPipeline
from source_tools.transcribers.whisper import WhisperTranscriber


@dataclass(frozen=True)
class TranscriberConfig:
    backend: str = "whisper"
    whisper_model: str = "base"
    groq_api_key: str | None = None
    nemotron_model_dir: str | None = None
    nemotron_language: str = "auto"
    include_fallbacks: bool = True


def build_transcriber(config: TranscriberConfig) -> Transcriber:
    backend = config.backend.lower()
    if backend == "whisper":
        return AudioPipeline(WhisperTranscriber(config.whisper_model))
    if backend == "groq":
        if not config.groq_api_key:
            raise ValueError("groq_api_key is required when backend='groq'")
        transcribers: list[Transcriber] = [AudioPipeline(GroqTranscriber(config.groq_api_key))]
        if config.include_fallbacks:
            if config.nemotron_model_dir:
                transcribers.append(AudioPipeline(NemotronTranscriber(config.nemotron_model_dir, config.nemotron_language)))
            transcribers.append(AudioPipeline(WhisperTranscriber(config.whisper_model)))
        return TranscriberPipeline(transcribers)
    if backend == "nemotron":
        if not config.nemotron_model_dir:
            raise ValueError("nemotron_model_dir is required when backend='nemotron'")
        transcribers = [AudioPipeline(NemotronTranscriber(config.nemotron_model_dir, config.nemotron_language))]
        if config.include_fallbacks:
            transcribers.append(AudioPipeline(WhisperTranscriber(config.whisper_model)))
        return TranscriberPipeline(transcribers)
    raise ValueError("backend must be one of: whisper, groq, nemotron")
