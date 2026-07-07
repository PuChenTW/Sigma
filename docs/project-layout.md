# AI Investment Research Studio — Project Layout

This repository contains the AI Investment Research Studio product plus the reusable `source_tools` tool layer.

## Layout

```text
src/
  studio_api/             FastAPI backend source
  studio_domain/          Product domain rules
  studio_schemas/         Shared Pydantic schemas
  studio_workflows/       Deterministic MVP research workflow
  source_tools/           Reusable source ingestion and media helpers

tests/
  source_tools/           Reusable tool-layer tests
  studio_api/             API scaffold and persistence tests
  studio_domain/          Domain rule tests
  studio_schemas/         Pydantic schema tests
  studio_workflows/       Workflow fixture and runner tests

frontend_prototype/       Design prototype reference
docs/                     Product, architecture, and planning docs
```

## Dependency Direction

Preferred direction:

```text
frontend/backend entrypoints
  -> src/studio_api
  -> src/studio_workflows
  -> src/studio_domain + src/studio_schemas
  -> src/source_tools where reusable ingestion/media helpers are needed
```

Trading committee integration should remain behind a future explicit boundary:

```text
src/studio_api
  -> src/studio_committee or src/studio_workflows
  -> external TradingAgents dependency if adopted
```

Avoid:

```text
src/source_tools -> apps
src/source_tools -> product workflow state
TradingAgents state -> Studio domain model
frontend_prototype -> production runtime dependency
```

## Scaffold Policy

Add directories only when implementing a concrete MVP slice. Avoid empty placeholder scaffolds.

When production app scaffolds are added:

- document install/dev/test/lint commands in `AGENTS.md`,
- keep Python packages imported from root `src/` during development unless a dedicated packaging task is introduced,
- use Context7 for current framework/API docs,
- verify frontend workflow with Playwright.
