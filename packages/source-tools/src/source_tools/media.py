import logging
import os
import re
import tempfile
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

import httpx

from source_tools.transcribers.base import Transcriber

logger = logging.getLogger(__name__)

MAX_TRANSCRIPT_BYTES = 500_000
MAX_TRANSCRIPT_CHARS = 100_000
MAX_AUDIO_BYTES = 500_000_000

_VTT_LINE = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3} --> .+$", re.MULTILINE)
_SRT_TIMECODE = re.compile(r"^\d+\s*\n\d{2}:\d{2}:\d{2},\d{3} --> .+\n", re.MULTILINE)
_AUDIO_MIME = re.compile(r"^audio/")


@dataclass(frozen=True)
class TranscriptContext:
    source_title: str = ""
    item_title: str = ""
    description: str = ""


Corrector = Callable[[str, TranscriptContext], Awaitable[str]]


def strip_timing_markers(text: str) -> str:
    text = _VTT_LINE.sub("", text)
    text = _SRT_TIMECODE.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def resolve_transcript_url(entry: dict[str, Any]) -> str | None:
    transcript = entry.get("podcast_transcript")
    if isinstance(transcript, dict) and transcript.get("url"):
        return transcript["url"]
    if isinstance(transcript, list) and transcript and transcript[0].get("url"):
        return transcript[0]["url"]
    for link in entry.get("links", []):
        if link.get("rel") == "transcript" and link.get("href"):
            return link["href"]
    return None


def extract_audio_url(entry: dict[str, Any]) -> str | None:
    for enclosure in entry.get("enclosures", []):
        href = enclosure.get("href") or enclosure.get("url")
        mime = enclosure.get("type", "")
        if href and _AUDIO_MIME.match(mime):
            return href
    return None


async def fetch_transcript_url(url: str) -> str | None:
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            async with client.stream("GET", url) as resp:
                resp.raise_for_status()
                content_type = resp.headers.get("content-type", "")
                chunks: list[bytes] = []
                total = 0
                async for chunk in resp.aiter_bytes(chunk_size=8192):
                    total += len(chunk)
                    if total > MAX_TRANSCRIPT_BYTES:
                        break
                    chunks.append(chunk)
        raw = b"".join(chunks).decode("utf-8", errors="replace")
        if "vtt" in content_type or "vtt" in url.lower() or "srt" in url.lower():
            return strip_timing_markers(raw)
        return raw
    except Exception as exc:
        logger.warning("Failed to fetch transcript %s: %s", url, exc)
        return None


async def download_audio(url: str) -> str | None:
    tmp = None
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".audio", delete=False)
        total = 0
        async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
            async with client.stream("GET", url) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_bytes(chunk_size=65536):
                    total += len(chunk)
                    if total > MAX_AUDIO_BYTES:
                        logger.warning("Audio file too large, aborting: %s", url)
                        tmp.close()
                        os.unlink(tmp.name)
                        return None
                    tmp.write(chunk)
        tmp.close()
        return tmp.name
    except Exception as exc:
        logger.warning("Failed to download audio %s: %s", url, exc)
        if tmp is not None:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass
        return None


async def extract_transcript(
    entry: dict[str, Any],
    transcriber: Transcriber | None = None,
    context: TranscriptContext | None = None,
    corrector: Corrector | None = None,
) -> str | None:
    context = context or TranscriptContext(
        item_title=entry.get("title", ""),
        description=entry.get("summary") or entry.get("description") or "",
    )

    async def _correct(text: str) -> str:
        if corrector is None:
            return text
        return await corrector(text, context)

    transcript_url = resolve_transcript_url(entry)
    if transcript_url:
        text = await fetch_transcript_url(transcript_url)
        if text:
            return await _correct(text[:MAX_TRANSCRIPT_CHARS])

    audio_url = extract_audio_url(entry)
    if audio_url and transcriber is not None:
        path = await download_audio(audio_url)
        if path:
            try:
                text = await transcriber.transcribe(path)
                if text:
                    return await _correct(text[:MAX_TRANSCRIPT_CHARS])
            finally:
                try:
                    os.unlink(path)
                except OSError:
                    pass
    return None
