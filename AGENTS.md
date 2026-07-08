# AGENTS.md instructions for /Users/chenpu/project/sigma

## Project Purpose

This repository is for **AI Investment Research Studio**.

The product is an AI-assisted investment research operating system. The user acts as a capital provider / investor / CIO who assigns open-ended research topics, inspects AI research progress, reviews evidence-backed theses, and decides whether research should be escalated into an investment decision.

This is not a stock chatbot, a single-ticker analyzer, an auto-trading bot, or a fixed multi-agent demo.

## Core Docs

Read these before major product or architecture work:

- `docs/product/north-star.md`: final product shape, target experience, product capabilities, and product boundaries.
- `docs/product/status-and-roadmap.md`: implemented status, limitations, commands, near-term roadmap, and expansion sequencing.
- `docs/product/evolution-plan.md`: staged path from the current MVP toward the prototype-like product experience.
- `docs/technical/architecture.md`: system boundaries, domain model, technical architecture, and integration rules.
- `docs/technical/api.md`: current API surface and API design rules.

## Current Repository State

| Path | Role |
|------|------|
| `src/studio_api/` | FastAPI backend app, routes, dependencies, and local persistence. |
| `src/studio_domain/` | Product domain rules and lifecycle checks. |
| `src/studio_schemas/` | API, persistence, and workflow Pydantic schemas. |
| `src/studio_workflows/` | Deterministic MVP research workflow, SMR fixtures, artifact generation, thesis synthesis, and committee proposal stub. |
| `src/source_tools/` | Independent reusable RSS, media/transcript, ASR fallback, and source-grounded LLM helpers; not part of the current Studio runtime path. |
| `frontend/` | Thin Next.js workflow UI and Playwright E2E test for the MVP research workflow. |
| `frontend_prototype/` | Design reference only; do not treat prototype runtime code as production architecture. |
| `tests/` | Focused Python tests for source tools, Studio API, schemas, domain rules, and workflows. |

Do not keep empty `apps/`, `packages/`, `services/`, or `vendor/` scaffold directories. Add concrete modules only when implementation needs them.

## Architecture Rules

- Keep `Research != InvestmentDecision`.
- Keep `Raw Evidence != ResearchArtifact`.
- Keep `Report != Thesis`.
- Keep `Role != Runtime Agent Instance`.
- Keep `Deterministic Computation != LLM Reasoning`.
- Keep `TradingAgents State != Studio Domain Model`.
- Treat TradingAgents as a future Trading Committee engine, not as the whole product.
- Keep route handlers thin and domain/workflow behavior in dedicated modules.

## `source_tools` Rules

- Keep `source_tools` independent from product auth, UI workflows, portfolio state, watchlists, report persistence, notification channels, and app settings.
- Library APIs must not read hidden app settings or `.env` internally. Pass model names, prompts, API keys, DSNs, source metadata, and runtime choices explicitly.
- Preserve source grounding. LLM helpers should keep evidence, inference, uncertainty, named entities, and numbers distinct.
- ASR provider dependencies belong behind optional extras.
- Basic RSS/media/AI helpers should not require local ASR packages.

## Code Philosophy

Simplicity beats cleverness. Delete aggressively.

- Think about performance from day one. Avoid O(n^2) when O(n) is straightforward.
- Do not abstract until there are at least 3 real use cases.
- Keep dependency layers shallow, ideally 2-3 layers.
- Make APIs hard to misuse and consistent.
- Get data structures right first; the code should follow naturally.

## Code Style

- Functions should do one thing and fit on screen.
- Prefer early returns.
- Avoid boolean arguments; model intent explicitly.
- Keep function arguments to 3 or fewer where practical.
- Names should reveal intent. Use short names only for short scopes.
- Comment why, not what.
- Remove commented-out code.
- Avoid dependency cycles.

## Commands

```bash
make sync
make sync-asr   # only when testing real ASR backends
make web-sync
make api
make web
make test-source-tools
make test-api
make test-e2e
make lint
make web-typecheck
make web-build
make format
make check
```

Local API JSON persistence defaults to `.local/studio-api.json`. Override it with `STUDIO_API_DATA_FILE` when needed.

## Testing Expectations

- Add or update focused tests for every public API change.
- Mock external network, ASR providers, market data providers, and LLM calls in tests.
- Run `make test-source-tools` before handing off `source_tools` changes.
- Run `make lint` for Python code edits.
- Run `make web-typecheck` for frontend edits.
- For frontend work, use Playwright to verify the actual user workflow, not only static rendering.

## Local Source Imports

`pyproject.toml` is configured with `tool.uv.package = false`, so local development does not build or install a local Studio or `source_tools` wheel. Python packages live under the root `src/` directory; pytest imports that source root through `pythonpath`, and API commands use `uvicorn --app-dir src`.

## Git Hygiene

- Do not commit `.venv/`, cache directories, `dist/`, or generated build output.
- Keep `source_tools` small and reusable.
- Keep TradingAgents integration behind a clear boundary so upstream changes remain manageable.
- Do not mix broad product scaffolding, tool-layer changes, and prototype cleanup in one change unless explicitly requested.
