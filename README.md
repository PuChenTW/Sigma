# AI Investment Research Studio

AI-assisted investment research operating system.

The user acts as a capital provider / investor / CIO: they assign open-ended research topics, inspect AI research team progress, review source-grounded theses, and decide whether a thesis should become an investment decision proposal.

This repository also contains `source_tools`, a reusable tool layer for RSS ingestion, transcript extraction, ASR fallback, and source-grounded LLM workflows.

## Product Docs

- [Codex design context](docs/ai-investment-research-studio-codex-context.md)
- [MVP scope](docs/ai-investment-research-studio-mvp-scope.md)
- [Project layout](docs/project-layout.md)

## Repository Layout

```text
apps/
  api/                    Backend API app boundary
  web/                    Frontend app boundary

packages/
  domain/                 Product domain model and lifecycle rules
  schemas/                API, persistence, and agent IO schemas
  source-tools/           Reusable RSS/media/transcript/LLM package

services/
  ingestion/              Evidence ingestion and normalization
  research-orchestrator/  Topic interpretation, task planning, desk coordination
  evidence-service/       Evidence storage and retrieval
  thesis-registry/        Thesis lifecycle and versioning
  trading-committee/      Bounded TradingAgents / committee wrapper

frontend_prototype/       Design prototype reference
docs/                     Product, architecture, and planning docs
vendor/                   Optional third-party vendored dependencies
```

## MVP

The first MVP validates one vertical slice:

```text
Topic
  -> Research Project
  -> Research Tasks
  -> Evidence
  -> Research Artifacts
  -> Thesis
  -> Trading Committee
  -> Decision Proposal
  -> User Approve / Reject
```

## Current Tool Layer Setup

The only executable package currently configured in `pyproject.toml` is `source_tools`, located at `packages/source-tools/src/source_tools`.

```bash
uv sync --group dev
```

Install ASR backends only when audio transcription is needed:

```bash
uv sync --group dev --extra asr
```

## `source_tools` Quick Start

```python
from source_tools import LLMConfig, TranscriptContext
from source_tools.ai import summarize_content
from source_tools.media import extract_transcript
from source_tools.rss import fetch_feed_items
from source_tools.transcribers import TranscriberConfig, build_transcriber

items = await fetch_feed_items(feed_url, limit=10)
item = items[0]

transcriber = build_transcriber(TranscriberConfig(backend="whisper", whisper_model="base"))
transcript = await extract_transcript(
    item.raw,
    transcriber=transcriber,
    context=TranscriptContext(source_title="Finance source", item_title=item.title, description=item.description),
)

summary = await summarize_content(
    item.title,
    transcript or item.description,
    LLMConfig(model=model, system_prompt=summary_prompt),
)
```

## Verify Current Code

```bash
uv run pytest packages/source-tools/tests -q
uv run ruff check .
uv build
```

When production `apps/api` or `apps/web` scaffolds are added, document their install, dev, lint, and test commands here and in `AGENTS.md`.
