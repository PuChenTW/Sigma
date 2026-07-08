# AI Investment Research Studio

AI-assisted investment research operating system.

The user acts as a capital provider / investor / CIO: they assign open-ended research topics, inspect AI research team progress, review source-grounded theses, and decide whether a thesis should become an investment decision proposal.

This repository also contains `source_tools`, a reusable tool layer for RSS ingestion, transcript extraction, ASR fallback, and source-grounded LLM workflows.

## Product Docs

- [Product](docs/product.md)
- [Architecture](docs/architecture.md)
- [Status and roadmap](docs/status-and-roadmap.md)

## Repository Layout

```text
src/
  studio_api/             FastAPI backend source
  studio_domain/          Product domain rules
  studio_schemas/         Shared Pydantic schemas
  studio_workflows/       Deterministic workflow and committee stub
  source_tools/           Reusable RSS/media/transcript/LLM package

tests/
  source_tools/           Reusable tool-layer tests
  studio_api/             API scaffold and persistence tests
  studio_domain/          Domain rule tests
  studio_schemas/         Pydantic schema tests
  studio_workflows/       Workflow and committee tests

frontend/                 Thin Next.js MVP workflow UI and Playwright test
frontend_prototype/       Design prototype reference
docs/                     Product, architecture, and planning docs
```

## MVP

The MVP validates one vertical slice:

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

`source_tools` is imported from local source during development, located at `src/source_tools`. The root `pyproject.toml` is configured with `tool.uv.package = false`, so `uv sync` does not build or install a local `source-tools` wheel.

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

## Verify

```bash
make check
make web-build
make test-e2e
```

Useful focused checks:

```bash
make test-source-tools
make test-api
make lint
make web-typecheck
```

## Local Development

```bash
make sync
make web-sync
make api
make web
```

Local JSON persistence defaults to `.local/studio-api.json`. Override it with `STUDIO_API_DATA_FILE` when needed.

The frontend reads the API base URL from `NEXT_PUBLIC_API_BASE_URL`; `make web` points it at the local FastAPI server.

## MVP Limitations

- Research output uses deterministic SMR fixtures; there is no live source discovery, market data, or LLM dependency in the demo path.
- The Trading Committee is a stubbed boundary that returns a structured proposal; it does not run TradingAgents.
- Approval or rejection records an investment decision only. It does not create trades, positions, or brokerage side effects.
- Local JSON persistence is for development and demo use, not production deployment.
