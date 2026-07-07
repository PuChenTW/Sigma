# AI Investment Research Studio — Project Layout

This repository contains the AI Investment Research Studio product plus the reusable `source_tools` tool layer.

## Layout

```text
apps/
  api/                    Backend API app boundary
  web/                    Frontend app boundary

src/
  studio_api/             FastAPI backend source
  studio_domain/          Product domain rules
  studio_schemas/         Shared Pydantic schemas
  source_tools/           Reusable source ingestion and media helpers

packages/
  domain/                 Product domain model and lifecycle rules
  schemas/                API, persistence, and agent IO schemas
  source-tools/           Reusable RSS/media/transcript/LLM tests and docs

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

## Dependency Direction

Preferred direction:

```text
apps
  -> services
  -> packages/domain + packages/schemas
  -> packages/source-tools where reusable ingestion/media helpers are needed
```

Trading committee integration should remain behind:

```text
apps/api
  -> services/trading-committee
  -> vendor/tradingagents or external TradingAgents dependency
```

Avoid:

```text
packages/source-tools -> apps
packages/source-tools -> services
TradingAgents state -> Studio domain model
frontend_prototype -> production runtime dependency
```

## Scaffold Policy

Directories start with README files rather than empty packages. Add executable code only when implementing a concrete MVP slice.

When production app scaffolds are added:

- document install/dev/test/lint commands in `AGENTS.md`,
- keep Python packages imported from root `src/` during development unless a dedicated packaging task is introduced,
- use Context7 for current framework/API docs,
- verify frontend workflow with Playwright.
