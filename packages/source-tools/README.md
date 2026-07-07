# Source Tools

Reusable Python package for source ingestion and source-grounded text workflows.

## Layout

```text
packages/source-tools/
  src/source_tools/       Importable Python package
  tests/                  Focused package tests
```

## Responsibility

- RSS / Atom fetching and normalization.
- Transcript URL resolution and transcript cleanup.
- Audio download and ASR fallback wiring.
- Source-grounded LLM helpers for summarization, correction, condensation, and chat.

## Not Responsibility

- Product auth, UI, portfolio state, watchlists, notifications, report persistence, or user workflows.
- Finance-specific prompts or investment recommendations.
- Hidden app settings or implicit `.env` loading.

## Verify

From the repository root:

```bash
uv run pytest packages/source-tools/tests -q
uv run ruff check .
uv build
```
