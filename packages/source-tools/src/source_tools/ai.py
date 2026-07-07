import asyncio
from collections.abc import AsyncIterator, Mapping
from dataclasses import dataclass, field
from functools import lru_cache

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage

DEFAULT_SUMMARY_PROMPT = (
    "You analyze source-grounded business and market content. Given a title and source text, produce a concise Markdown brief. "
    "Separate facts from interpretation, preserve important numbers and named entities, and call out uncertainty when evidence is thin."
)
DEFAULT_CHAT_PROMPT = (
    "You are a source-grounded analysis partner. Answer using the provided context first, distinguish evidence from inference, "
    "and say when the context is insufficient."
)
DEFAULT_CORRECTION_PROMPT = (
    "Correct ASR and transcript errors using the provided context. Preserve factual claims, names, numbers, and speaker meaning. "
    "Return only the corrected text."
)
DEFAULT_CONDENSER_PROMPT = (
    "Condense the provided text while preserving named entities, numbers, factual claims, arguments, risks, and conclusions. "
    "Remove filler and repetition. Return only the condensed text."
)

DEFAULT_CHUNK_CHARS = 12_000
DEFAULT_CONTEXT_TEXT_LIMIT = 12_000


@dataclass(frozen=True)
class LLMConfig:
    """Explicit LLM configuration for library users.

    `model` is the pydantic-ai model string, for example `google-gla:gemini-flash-lite-latest`.
    """

    model: str
    system_prompt: str


@dataclass(frozen=True)
class TextContext:
    source_title: str = ""
    item_title: str = ""
    description: str = ""
    summary: str | None = None
    transcript: str | None = None
    content: str | None = None
    language: str = "zh-TW"
    metadata: Mapping[str, str] = field(default_factory=dict)


@lru_cache(maxsize=64)
def _get_agent(model: str, system_prompt: str) -> Agent:
    return Agent(model, instructions=system_prompt)


def split_text_chunks(text: str, max_chars: int = DEFAULT_CHUNK_CHARS) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for para in paragraphs:
        while len(para) > max_chars:
            chunks.append(para[:max_chars])
            para = para[max_chars:]
        sep = "\n\n" if current else ""
        if current and current_len + len(sep) + len(para) > max_chars:
            chunks.append("\n\n".join(current))
            current = []
            current_len = 0
        current.append(para)
        current_len += len(sep) + len(para)
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def _context_header(context: TextContext) -> str:
    lines = []
    if context.source_title:
        lines.append(f"Source: {context.source_title}")
    if context.item_title:
        lines.append(f"Item: {context.item_title}")
    if context.description:
        lines.append(f"Description: {context.description}")
    for key, value in context.metadata.items():
        lines.append(f"{key}: {value}")
    return "\n".join(lines)


def _chat_context(context: TextContext, text_limit: int) -> str:
    parts = []
    header = _context_header(context)
    if header:
        parts.append(header)
    if context.summary:
        parts.append(f"Summary:\n{context.summary}")
    source_text = context.transcript or context.content
    if source_text:
        parts.append(f"Source text:\n{source_text[:text_limit]}")
    if not parts:
        parts.append("No source text was provided.")
    parts.append(f"Preferred UI language: {context.language}")
    return "\n\n".join(parts)


async def run_text_prompt(prompt: str, config: LLMConfig) -> str:
    agent = _get_agent(config.model, config.system_prompt)
    result = await agent.run(prompt)
    return result.output


async def summarize_content(title: str, content: str, config: LLMConfig) -> str:
    prompt = f"Title: {title}\n\nSource text:\n{content}"
    return await run_text_prompt(prompt, config)


async def correct_text(text: str, context: TextContext, config: LLMConfig, chunk_chars: int = DEFAULT_CHUNK_CHARS) -> str:
    chunks = split_text_chunks(text, chunk_chars)
    header = _context_header(context)

    async def _correct(chunk: str) -> str:
        prompt = f"{header}\n\nText:\n{chunk}" if header else f"Text:\n{chunk}"
        return await run_text_prompt(prompt, config)

    if len(chunks) == 1:
        return await _correct(chunks[0])
    return "\n\n".join(await asyncio.gather(*[_correct(chunk) for chunk in chunks]))


async def condense_text(text: str, context: TextContext, config: LLMConfig) -> str:
    header = _context_header(context)
    prompt = f"{header}\n\nText:\n{text}" if header else f"Text:\n{text}"
    return await run_text_prompt(prompt, config)


async def chat_with_context(
    user_message: str,
    context: TextContext,
    config: LLMConfig,
    history: list[ModelMessage] | None = None,
    text_limit: int = DEFAULT_CONTEXT_TEXT_LIMIT,
) -> tuple[str, list[ModelMessage]]:
    system_prompt = f"{config.system_prompt}\n\nContext:\n{_chat_context(context, text_limit)}"
    agent = _get_agent(config.model, system_prompt)
    result = await agent.run(user_message, message_history=history or None)
    return result.output, list(result.all_messages())


async def chat_with_context_stream(
    user_message: str,
    context: TextContext,
    config: LLMConfig,
    history: list[ModelMessage] | None = None,
    text_limit: int = DEFAULT_CONTEXT_TEXT_LIMIT,
) -> AsyncIterator[tuple[str, list[ModelMessage] | None]]:
    system_prompt = f"{config.system_prompt}\n\nContext:\n{_chat_context(context, text_limit)}"
    agent = _get_agent(config.model, system_prompt)
    async with agent.run_stream(user_message, message_history=history or None) as result:
        async for chunk in result.stream_text(delta=True):
            yield chunk, None
        yield "", list(result.all_messages())
