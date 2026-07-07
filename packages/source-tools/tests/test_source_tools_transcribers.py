import pytest
from source_tools.transcribers import AudioPipeline, TranscriberConfig, TranscriberPipeline, build_transcriber


def test_build_whisper_transcriber():
    transcriber = build_transcriber(TranscriberConfig(backend="whisper", whisper_model="base"))

    assert isinstance(transcriber, AudioPipeline)


def test_build_groq_requires_key():
    with pytest.raises(ValueError, match="groq_api_key"):
        build_transcriber(TranscriberConfig(backend="groq"))


def test_build_groq_pipeline_with_fallbacks():
    transcriber = build_transcriber(TranscriberConfig(backend="groq", groq_api_key="key", nemotron_model_dir="/models/nemo"))

    assert isinstance(transcriber, TranscriberPipeline)


def test_build_unknown_backend_fails():
    with pytest.raises(ValueError, match="backend"):
        build_transcriber(TranscriberConfig(backend="bogus"))
