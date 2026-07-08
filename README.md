# AI Investment Research Studio

AI-assisted investment research operating system.

The user acts as a capital provider / investor / CIO: they assign open-ended research topics, inspect AI research team progress, review source-grounded theses, and decide whether a thesis should become an investment decision proposal.

This repository also contains `source_tools`, a reusable tool layer for RSS ingestion, transcript extraction, ASR fallback, and source-grounded LLM workflows.

## Product Docs

- [Documentation index](docs/README.md)
- [Product north star](docs/product/north-star.md)
- [Status and roadmap](docs/product/status-and-roadmap.md)
- [Product evolution plan](docs/product/evolution-plan.md)
- [Architecture](docs/technical/architecture.md)
- [API design](docs/technical/api.md)

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
docs/product/             Product north star, status, roadmap, and evolution plan
docs/technical/           Architecture, API design, and technical records
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
make install-hooks
make web-sync
make api
make web
```

Local JSON persistence defaults to `.local/studio-api.json`. Override it with `STUDIO_API_DATA_FILE` when needed.

The frontend reads the API base URL from `NEXT_PUBLIC_API_BASE_URL`; `make web` points it at the local FastAPI server.

## Evidence Workbench Manual Smoke Test

Start the local API and web UI in separate terminals:

```bash
make api
make web
```

Then open the web UI and verify this path:

1. Create a project with an SMR-related topic.
2. In Evidence workbench, add one `Article` or `Note` for the `Industry` desk with title, summary, citation excerpt, and location.
3. Confirm the evidence library shows the new source and citation preview.
4. Click `Run research`.
5. In `Artifacts and citations`, confirm the industry artifact citation shows the user-added evidence title, summary, and citation excerpt.

Existing committee approve/reject can be smoke-tested after this by clicking `Committee`, entering an optional decision note, and approving or rejecting the proposal. That path is not required to validate Evidence Workbench scope.

## MVP Limitations

- Research output is still deterministic. User evidence affects citation selection, while artifact and thesis prose are not yet generated from live source analysis.
- Evidence entry is currently manual. There is no server-side URL fetching, article extraction, PDF parsing, transcript ingestion, RSS discovery, market data, or LLM dependency in the demo path.
- The Trading Committee is a stubbed boundary that returns a structured proposal; it does not run TradingAgents.
- Approval or rejection records an investment decision only. It does not create trades, positions, or brokerage side effects.
- Local JSON persistence is for development and demo use, not production deployment.
