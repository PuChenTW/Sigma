from unittest.mock import AsyncMock, patch

import pytest

from source_tools.media import TranscriptContext, extract_audio_url, extract_transcript, resolve_transcript_url, strip_timing_markers


def test_strip_timing_markers_supports_vtt_and_srt():
    assert strip_timing_markers("00:00:01.000 --> 00:00:02.000\nHello") == "Hello"
    assert strip_timing_markers("1\n00:00:01,000 --> 00:00:02,000\nWorld") == "World"


def test_resolve_transcript_url_from_feed_entry():
    assert resolve_transcript_url({"podcast_transcript": {"url": "https://example.com/t.vtt"}}) == "https://example.com/t.vtt"
    assert resolve_transcript_url({"links": [{"rel": "transcript", "href": "https://example.com/t.srt"}]}) == "https://example.com/t.srt"


def test_extract_audio_url_requires_audio_mime():
    entry = {"enclosures": [{"href": "https://example.com/audio.mp3", "type": "audio/mpeg"}, {"href": "https://example.com/image.jpg", "type": "image/jpeg"}]}
    assert extract_audio_url(entry) == "https://example.com/audio.mp3"


@pytest.mark.asyncio
async def test_extract_transcript_prefers_transcript_url_and_corrects():
    entry = {"title": "Item", "summary": "Desc", "podcast_transcript": {"url": "https://example.com/t.txt"}}
    corrector = AsyncMock(return_value="corrected")

    with patch("source_tools.media.fetch_transcript_url", AsyncMock(return_value="raw")):
        out = await extract_transcript(entry, context=TranscriptContext(source_title="Source"), corrector=corrector)

    assert out == "corrected"
    corrector.assert_awaited_once()
    assert corrector.call_args.args[1].source_title == "Source"


@pytest.mark.asyncio
async def test_extract_transcript_uses_audio_when_no_transcript_url():
    transcriber = AsyncMock()
    transcriber.transcribe = AsyncMock(return_value="audio text")

    with (
        patch("source_tools.media.download_audio", AsyncMock(return_value="/tmp/audio.mp3")),
        patch("source_tools.media.os.unlink"),
    ):
        out = await extract_transcript({"enclosures": [{"href": "https://example.com/a.mp3", "type": "audio/mpeg"}]}, transcriber=transcriber)

    assert out == "audio text"
    transcriber.transcribe.assert_awaited_once_with("/tmp/audio.mp3")
