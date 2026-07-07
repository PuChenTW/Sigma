from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from source_tools.ai import LLMConfig, TextContext, chat_with_context_stream, correct_text, split_text_chunks, summarize_content


def test_split_text_chunks_preserves_limit():
    para = "x" * 6_000
    chunks = split_text_chunks("\n\n".join([para] * 4), max_chars=12_000)

    assert len(chunks) > 1
    assert all(len(chunk) <= 12_000 for chunk in chunks)


@pytest.mark.asyncio
async def test_summarize_content_uses_explicit_config():
    result = MagicMock(output="brief")
    agent = MagicMock()
    agent.run = AsyncMock(return_value=result)

    with patch("source_tools.ai._get_agent", return_value=agent) as get_agent:
        out = await summarize_content("Title", "Source text", LLMConfig(model="test:model", system_prompt="Analyze"))

    assert out == "brief"
    get_agent.assert_called_once_with("test:model", "Analyze")
    assert "Title" in agent.run.call_args.args[0]
    assert "Source text" in agent.run.call_args.args[0]


@pytest.mark.asyncio
async def test_correct_text_chunks_with_context():
    calls = []

    async def fake_run(prompt, config):
        calls.append(prompt)
        return "ok"

    text = "\n\n".join(["a" * 10] * 4)
    with patch("source_tools.ai.run_text_prompt", side_effect=fake_run):
        out = await correct_text(
            text,
            TextContext(source_title="Source", item_title="Item", metadata={"Ticker": "AAPL"}),
            LLMConfig(model="test:model", system_prompt="Correct"),
            chunk_chars=20,
        )

    assert out == "ok\n\nok\n\nok\n\nok"
    assert len(calls) == 4
    assert "Source: Source" in calls[0]
    assert "Ticker: AAPL" in calls[0]


@pytest.mark.asyncio
async def test_chat_with_context_stream_yields_deltas_then_history():
    async def fake_text_stream():
        yield "a"
        yield "b"

    streamed = MagicMock()
    streamed.stream_text = MagicMock(return_value=fake_text_stream())
    streamed.all_messages = MagicMock(return_value=[])

    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=streamed)
    cm.__aexit__ = AsyncMock(return_value=False)

    agent = MagicMock()
    agent.run_stream = MagicMock(return_value=cm)

    with patch("source_tools.ai._get_agent", return_value=agent):
        chunks = []
        async for item in chat_with_context_stream(
            "question",
            TextContext(source_title="Source", item_title="Item", summary="Summary"),
            LLMConfig(model="test:model", system_prompt="Chat"),
        ):
            chunks.append(item)

    assert chunks == [("a", None), ("b", None), ("", [])]
