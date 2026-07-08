# Status And Roadmap

This document tracks what the repository currently supports and where the next useful work likely is.

## Current Status

The MVP vertical slice is implemented as a deterministic local demo:

```text
Topic
  -> Research Project
  -> Research Tasks
  -> User Evidence / Curated Fallback Evidence
  -> Research Artifacts
  -> Thesis
  -> Decision Proposal
  -> Approve / Reject
  -> Investment Decision
```

Implemented areas:

- FastAPI backend under `src/studio_api`.
- Shared Pydantic schemas under `src/studio_schemas`.
- Domain transition rules under `src/studio_domain`.
- Deterministic workflow runner under `src/studio_workflows`.
- Curated SMR evidence fixtures.
- Project-scoped Evidence Workbench for manual note/article evidence creation.
- Runner policy that prefers cited user evidence by desk and uses curated fixtures only for missing desk coverage.
- Cited artifact generation.
- Thesis synthesis with candidate asset rationale.
- Trading Committee stub behind an explicit interface.
- Proposal approve/reject endpoints and persisted decision records.
- Thin Next.js workflow UI under `frontend`.
- Playwright E2E coverage for the primary approve/reject paths and user evidence traceability.
- Local source import for `src/source_tools` without building a local wheel.
- Makefile commands for common development, test, lint, build, and E2E flows.

## Current Limitations

- Research output is still deterministic; user evidence affects citation selection, but artifact and thesis prose are not yet generated from live source analysis.
- Evidence entry is manual only. There is no server-side URL fetching, article extraction, PDF parsing, transcript ingestion, RSS discovery, market data, or LLM dependency in the demo path.
- The Trading Committee is a stub and does not run TradingAgents.
- Approval or rejection records an investment decision only. It does not create trades, positions, or brokerage side effects.
- Local JSON persistence is for development and demo use, not production deployment.
- There is no production auth, background job system, deployment story, or observability stack.
- The UI is a workflow proof, not a full dashboard or design system.

## Useful Commands

Install dependencies:

```bash
make sync
make web-sync
```

Run locally:

```bash
make api
make web
```

Verify:

```bash
make check
make web-build
make test-e2e
```

Focused checks:

```bash
make test-source-tools
make test-api
make lint
make web-typecheck
```

Local API JSON persistence defaults to `.local/studio-api.json`. Override it with `STUDIO_API_DATA_FILE` when needed.

## Recommended Next Direction

The next step should deliberately choose one axis of progress instead of expanding everything at once.

Recommended order:

1. Improve research realism.
2. Improve evidence and retrieval.
3. Integrate a real committee engine.
4. Add durable infrastructure only when the workflow requires it.
5. Expand portfolio and position workflows after decision quality is useful.

## Option A: Improve Research Realism

Goal:

- Move beyond deterministic SMR text while preserving citation discipline.

Possible work:

- Add URL/article ingestion that extracts title, body text, source metadata, and candidate citation excerpts.
- Add PDF/uploaded document ingestion with page-aware citation locations.
- Add RSS/transcript ingestion into project evidence after the URL and document path is stable.
- Add an evidence review queue so system-proposed summaries and excerpts are approved or corrected before research uses them.
- Add optional schema-validated LLM artifact generation grounded only in approved evidence.
- Keep deterministic fixtures as test fallback.
- Preserve validation that generated artifacts and theses cannot cite missing or foreign evidence.

This is likely the highest-value next direction because it tests whether the product remains trustworthy with real inputs.

## Option B: Improve Evidence Storage And Retrieval

Goal:

- Make evidence usable across more projects and sources.

Possible work:

- Move from JSON persistence to PostgreSQL.
- Add normalized source and citation tables.
- Add PostgreSQL full-text search.
- Add embeddings and `pgvector` only after source volume justifies it.
- Add retrieval tests that prove citations resolve to original evidence.

Do this before broad source ingestion becomes too large for local JSON.

## Option C: Integrate TradingAgents Behind Committee Boundary

Goal:

- Replace the proposal stub without letting TradingAgents own the Studio domain.

Possible work:

- Keep the existing committee input/output contract.
- Map selected thesis, artifacts, citations, and portfolio context into TradingAgents-compatible input.
- Convert TradingAgents output back into `DecisionProposal`.
- Add contract tests proving Studio objects do not depend on TradingAgents state.

This should happen after the proposal contract is stable.

## Option D: Productize The Workflow UI

Goal:

- Make the workflow easier to use without turning it into a broad dashboard project.

Possible work:

- Improve project navigation and persisted project switching.
- Add clearer evidence and citation inspection.
- Add thesis challenge/refinement actions.
- Add proposal history and decision history views.
- Keep portfolio dashboards and position management deferred.

Use Playwright for every meaningful frontend workflow change.

## Option E: Production Readiness

Goal:

- Prepare for hosted or multi-user usage.

Possible work:

- Add production configuration.
- Add auth only when there is more than one real user or hosted access.
- Add background jobs when workflows become long-running.
- Add structured observability once LLM/agent steps are real.
- Add deployment documentation after runtime architecture stabilizes.

Do not start here unless deployment is the immediate product need.

## Near-Term Recommendation

The most pragmatic next milestone is:

```text
Real evidence ingestion
  -> evidence review queue
  -> cited artifact generation
  -> thesis validation
  -> same committee proposal contract
  -> same Playwright E2E workflow
```

This keeps the current vertical slice intact while replacing the least realistic part of the post-MVP demo: manual evidence entry and deterministic research text.
