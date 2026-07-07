# AGENTS.md instructions for /Users/chenpu/project/sigma

## Project Purpose

This repository is for **AI Investment Research Studio**.

The product is an AI-assisted investment research operating system. The user acts as a capital provider / investor / CIO who can assign open-ended research topics, inspect what the AI research team is doing, review evidence-backed theses, challenge or refine conclusions, and decide whether research should be escalated into an investment decision.

This is not a stock chatbot, a single-ticker analyzer, an auto-trading bot, or a fixed multi-agent demo.

## Current Repository State

| Path | Role |
|------|------|
| `docs/ai-investment-research-studio-codex-context.md` | Primary product and architecture context. Read this before major design work. |
| `docs/ai-investment-research-studio-mvp-scope.md` | MVP scope, vertical slice, in/out of scope, and acceptance criteria. |
| `docs/project-layout.md` | Repository layout and dependency direction. |
| `src/studio_api/` | FastAPI backend app scaffold and local persistence. |
| `src/studio_domain/` | Product domain rules. |
| `src/studio_schemas/` | API, persistence, and workflow schemas. |
| `src/studio_workflows/` | Deterministic MVP task planning, SMR fixtures, artifact generation, and thesis synthesis. |
| `src/source_tools/` | Reusable RSS, media/transcript, ASR fallback, and source-grounded LLM helpers. |
| `frontend_prototype/` | Claude Design frontend prototype showing intended UX. Treat as product/design reference, not production code. |
| `tests/` | Focused Python tests for source tools and Studio MVP foundation. |

`source_tools` is useful infrastructure, but it is not the product. Do not force product concepts into `source_tools`; keep it reusable unless there is a clear tool-layer API need.

## Product Model

The product should help the user manage a research team:

1. Submit a free-form topic or external source without first choosing a ticker.
2. Let a CIO / Chief of Staff layer interpret intent, create a research project, and plan tasks.
3. Assign work to research desks such as Industry, Macro, Fundamental, Market Intelligence, Quant / Technical, and Narrative.
4. Track research tasks, status, blockers, and agent activity.
5. Ingest and preserve evidence from media, articles, transcripts, PDFs, notes, market data, and other sources.
6. Produce research artifacts and evolve them into versioned investment theses.
7. Escalate selected theses and assets into a Trading Committee for a bounded investment decision.
8. Track decisions, positions, outcomes, and feedback over time.

## Frontend Prototype Intent

The prototype in `frontend_prototype/投資工作室.dc.html` establishes the first product shape:

- **Dashboard**: portfolio snapshot, team status, active research, current positions, pending decisions.
- **Assign Task**: user submits a topic, selects research facets, sets priority, and sees a task queue.
- **Research Reports**: thesis list and thesis detail with key points, narrative, data points, and related trades.
- **Decision Desk**: trader proposals awaiting user approval or rejection, with entry, sizing, take-profit, stop-loss, risk, conviction, rationale, and supporting theses.
- **Positions**: active trades with risk controls, catalysts, related theses, and status reporting.

When building production UI, preserve this workflow intent. Do not treat the prototype runtime (`support.js`) as application architecture.

## Architecture Direction

The core boundary is:

```text
Investment Research Studio
  -> Research OS
  -> Research Desks
  -> Thesis Registry
  -> Evidence Store
  -> Trading Committee
  -> TradingAgents
```

Current repository scaffold:

```text
src/
  studio_api/
  studio_domain/
  studio_schemas/
  studio_workflows/
  source_tools/
tests/
  studio_workflows/
```

TradingAgents should be treated as a **Trading Committee Engine**, not as the whole product.

Prefer wrapping or isolating TradingAgents behind a bounded service/API. Avoid deeply forking it or making its graph state become the Studio domain model.

Recommended technical direction from the product context:

- Frontend: `Next.js`
- Backend API: `FastAPI`
- Domain schemas: `Pydantic`
- Research orchestration: evaluate `PydanticAI` vs `LangGraph`; current bias is PydanticAI for open-ended research and LangGraph / TradingAgents for bounded committee workflow.
- Main persistence: `PostgreSQL`
- Evidence retrieval: PostgreSQL FTS + `pgvector` + hybrid retrieval / RRF
- Raw media storage: S3 / MinIO
- Background jobs: Celery initially; Temporal later only if complexity justifies it.
- Observability: Langfuse and OpenTelemetry when agent workflows become real.

Use Context7 for current library/API documentation. Use Playwright for frontend development, testing, and debugging.

## Domain Boundaries

Keep these concepts separate:

- `Research != InvestmentDecision`
- `Raw Evidence != ResearchArtifact`
- `Report != Thesis`
- `Role != Runtime Agent Instance`
- `Deterministic Computation != LLM Reasoning`
- `TradingAgents State != Studio Domain Model`

Core Studio entities should include:

- `ResearchProject`
- `ResearchTask`
- `Evidence`
- `EvidenceCitation`
- `ResearchArtifact`
- `Thesis`
- `InvestmentDecision`
- `Position`
- `ActivityEvent`

Thesis objects need lifecycle and versioning. A thesis is not just a generated report; it should carry claims, evidence for and against, assumptions, catalysts, invalidation conditions, horizon, confidence, status, and outcome.

## MVP Direction

The first MVP should be a minimal vertical slice:

```text
User submits topic
  -> CIO creates one research project
  -> 2-3 desks produce source-grounded artifacts
  -> System creates one thesis
  -> User reviews thesis
  -> One selected ticker/asset goes to Trading Committee
  -> System returns a decision proposal
  -> User approves or rejects
```

For example:

```text
SMR topic
  -> Industry + Macro + Fundamental research
  -> Thesis
  -> OKLO / SMR / CCJ candidate selection
  -> Trading Committee decision
```

Do not start by building every dashboard widget, every asset class, full autonomous research, or automated trading. The MVP should prove that topic-driven research can become an auditable, evidence-backed thesis and then a bounded investment decision.

## `source_tools` Rules

- Keep `source_tools` independent from product auth, UI workflows, portfolio state, watchlists, report persistence, notification channels, and app settings.
- Library APIs must not read hidden app settings or `.env` internally. Pass model names, prompts, API keys, DSNs, source metadata, and runtime choices explicitly.
- Preserve source grounding. LLM helpers should keep evidence, inference, uncertainty, named entities, and numbers distinct.
- ASR provider dependencies belong behind optional extras. Basic RSS/media/AI helpers should not require local ASR packages.

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
make api
make test-source-tools
make test-api
make lint
make format
make check
```

Local API JSON persistence defaults to `.local/studio-api.json`. Override it with `STUDIO_API_DATA_FILE` when needed.

## Testing Expectations

- Add or update focused tests for every public API change.
- Mock external network, ASR providers, market data providers, and LLM calls in tests.
- Run `make test-source-tools` before handing off `source_tools` changes.
- Run `make lint` for Python code edits.
- For frontend work, use Playwright to verify the actual user workflow, not only static rendering.

## Local Source Imports

`pyproject.toml` is configured with `tool.uv.package = false`, so local development does not build or install a `source_tools` wheel. Python packages live under the root `src/` directory; pytest imports that source root through `pythonpath`, and API commands use `uvicorn --app-dir src`.

## Git Hygiene

- Do not commit `.venv/`, cache directories, `dist/`, or generated build output.
- Keep `source_tools` small and reusable.
- Keep TradingAgents integration behind a clear boundary so upstream changes remain manageable.
- Do not mix broad product scaffolding, tool-layer changes, and prototype cleanup in one change unless explicitly requested.
