# Status And Roadmap

This document tracks what the repository currently supports and where the next useful work likely is.

Product north star: `docs/product/north-star.md`.
Evolution plan: `docs/product/evolution-plan.md`.

## Current Status

The MVP vertical slice is implemented as a deterministic local research workflow:

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
- Project creation currently accepts a free-form `topic` only; `priority`, `facets`, task dependencies, and blockers are P1 concepts, not current API fields.
- Project-scoped evidence and citation API contracts for source-grounded traceability; the standalone frontend Evidence Workbench has been removed.
- Runner policy that prefers cited user evidence by desk and uses curated fixtures only for missing desk coverage.
- Cited artifact generation.
- Thesis synthesis with candidate asset rationale.
- Trading Committee stub behind an explicit interface.
- Proposal approve/reject endpoints and persisted decision records.
- Research workflow run endpoint: `POST /research-projects/{project_id}/run-research`.
- Next.js UI under `frontend` now uses a prototype-aligned workspace shell with dashboard, research workspace, Decision Desk, position preview, and assignment views.
- The research workflow, citation trace, committee evaluation, and approve/reject paths are API-backed; dashboard aggregates API-backed project/artifact/proposal state where available.
- Prototype-parity surfaces for broader report library, position workspace, team status, and assignment facets are currently mock-backed previews until the matching API/domain records exist.
- Playwright E2E coverage for the primary approve/reject paths and user evidence traceability.
- `src/source_tools` is retained as independent reusable source infrastructure; the current Studio MVP runtime does not depend on it.
- Makefile commands for common development, test, lint, build, and E2E flows.

## Current Limitations

- Research output is still deterministic; user evidence affects citation selection, but artifact and thesis prose are not yet generated from live source analysis.
- Evidence entry exists only as backend API infrastructure. There is no standalone frontend workbench, server-side URL fetching, article extraction, PDF parsing, transcript ingestion, RSS discovery, market data, or LLM dependency in the current Studio workflow.
- The Trading Committee is a stub and does not run TradingAgents.
- Approval or rejection records an investment decision only. It does not create trades, positions, or brokerage side effects.
- The UI now exposes prototype-like dashboard, research, decision, position, and assignment surfaces, but several are preview-only and not yet backed by durable domain/API records.
- There is still no API-backed Chief of Staff / CIO Router, task dependency graph, blocker state, thesis challenge/refinement loop, multiple-proposal queue, position lifecycle, or execution reporting flow.
- The visible research team model is a frontend preview; backend task ownership is still limited to the current deterministic desk tasks.
- Local JSON persistence is for development and demo use, not production deployment.
- There is no production auth, background job system, deployment story, or observability stack.
- The UI is moving from workflow proof toward prototype parity, but the API contract and domain records for the broader workspace are not complete.

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

The next step should deliberately choose one axis of progress instead of expanding everything at once. `frontend_prototype/` should guide the target experience, but implementation should move through the phase gates in `docs/product/evolution-plan.md`.

The product-facing priority is the research operating system experience: free-form topic intake, Chief of Staff planning, desk-level task ownership, task status/blockers/activity, and a thesis challenge loop. Evidence ingestion and citation approval are important trust infrastructure, but they should support that workflow rather than become the user's main job.

The prototype's trading dashboard, active positions, and execution flows are later-stage expressions of the same product, not the immediate build target. They should not pull the roadmap toward auto-trading, portfolio accounting, or a ticker-first workflow. Near-term UI work should make the Studio feel like a research team workspace before it feels like a portfolio terminal.

Recommended order:

1. Convert the prototype-aligned frontend previews into API-backed records in priority order: research team routing, desk tasks, blockers, activity, and project switching.
2. Add thesis challenge/refinement and richer desk artifacts so the user can steer research before a decision proposal exists.
3. Improve source intake and evidence traceability where the workspace needs it: task intake attachments, challenge/refinement attachments, URLs, notes, transcripts/PDFs later, cited excerpts, and validation that claims resolve to approved or explicit evidence.
4. Allow multiple proposals and a richer Decision Desk once thesis/proposal traceability remains solid.
5. Add user-entered paper/manual position tracking after approved decisions have useful lifecycle semantics.
6. Add market data, portfolio dashboards, durable infrastructure, real committee engines, and production concerns only when the workflow requires them.

## Current Product Plan

The detailed phase plan lives in `docs/product/evolution-plan.md`.

Current stance:

- P0 is implemented as a deterministic local research workflow.
- P1 should be corrected to Research Team Workspace: a product-facing milestone that makes the Studio feel like managing an AI research team.
- The frontend shell now previews that P1 shape, but the product milestone is not complete until its visible team, assignment, blocker, challenge, and activity concepts are backed by durable API/domain records.
- Real evidence ingestion and approval should become an enabling trust slice inside or after the workspace milestone, not the whole product-facing P1.
- New evidence capture should be integrated into research task intake and thesis challenge/refinement flows, not restored as a separate top-level workbench.
- P3-P5 should wait until proposal traceability, decision lifecycle, and paper position semantics are stable.

Do not start a later phase only to make the UI look complete. Start it when the earlier phase has a working end-to-end path, focused tests, and clear domain records to aggregate.

## Option A: Build Research Team Workspace

Goal:

- Make the product feel like an AI research operating system instead of a single workflow proof.

Possible work:

- Add a Chief of Staff / CIO Router that turns a free-form topic into a project objective and desk-scoped research tasks.
- Back the prototype-style research team board with real desks, assigned tasks, statuses, blockers, dependencies, and activity.
- Expand fixed desks toward the original product model: Industry, Macro, Fundamental, Market Intelligence, Quant / Technical, and Narrative.
- Add thesis detail actions for challenge, refine, request-more-research, and record why a thesis changed.
- Keep deterministic task planning/artifact generation as the testable baseline until agentic research is introduced.
- Preserve source/citation lineage for every artifact and thesis; evidence review is used where a claim needs trust, not as a line-by-line document approval workflow.

This is the highest-value product direction because it closes the biggest gap from the original concept: the user should feel like they are managing a research team, not manually approving extracted snippets.

## Option B: Improve Research Realism And Evidence Traceability

Goal:

- Move beyond deterministic SMR text while preserving citation discipline.

Possible work:

- Add URL/article ingestion that extracts title, body text, source metadata, and candidate citation excerpts.
- Add uploaded notes/documents, then PDF/transcript ingestion after the simpler source path is stable.
- Add evidence review for cited excerpts and high-impact claims.
- Add optional schema-validated LLM artifact generation grounded only in project evidence.
- Keep deterministic fixtures as test fallback.
- Preserve validation that generated artifacts and theses cannot cite missing or foreign evidence.

Do this as an enabling slice for the research workspace. Avoid making the user's primary flow "approve every excerpt before research can happen."

## Option C: Improve Evidence Storage And Retrieval

Goal:

- Make evidence usable across more projects and sources.

Possible work:

- Move from JSON persistence to PostgreSQL.
- Add normalized source and citation tables.
- Add PostgreSQL full-text search.
- Add embeddings and `pgvector` only after source volume justifies it.
- Add retrieval tests that prove citations resolve to original evidence.

Do this before broad source ingestion becomes too large for local JSON.

## Option D: Integrate TradingAgents Behind Committee Boundary

Goal:

- Replace the proposal stub without letting TradingAgents own the Studio domain.

Possible work:

- Keep the existing committee input/output contract.
- Map selected thesis, artifacts, citations, and portfolio context into TradingAgents-compatible input.
- Convert TradingAgents output back into `DecisionProposal`.
- Add contract tests proving Studio objects do not depend on TradingAgents state.

This should happen after the proposal contract is stable and after P1/P2 produce durable research tasks, artifacts, theses, and citation context worth evaluating. Do not start with a TradingAgents fork or vendor tree as the main product axis.

## Option E: Productize The Workflow UI

Goal:

- Turn the prototype-aligned frontend shell into an API-backed workflow without letting mock-backed dashboard surfaces define false product state.

Possible work:

- Improve project navigation and persisted project switching.
- Add clearer evidence and citation inspection.
- Add thesis challenge/refinement actions.
- Add proposal history and decision history views.
- Keep portfolio dashboards and position management preview-only until approved decisions have useful lifecycle semantics.
- Keep frontend data adapters explicit: existing API-backed workflow state should stay separate from mock-backed preview data.
- Do not reintroduce a standalone Evidence Workbench; source intake belongs inside assignment and thesis-review workflows.

Use Playwright for every meaningful frontend workflow change.

## Option F: Production Readiness

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

The most pragmatic next milestone for aligning the product with the original concept and `frontend_prototype/` is P1 Research Team Workspace:

```text
Free-form topic
  -> Chief of Staff / CIO Router
  -> desk-scoped research tasks
  -> team status / blockers / activity
  -> desk artifacts
  -> thesis challenge / refinement
  -> same committee proposal contract
```

This keeps the current vertical slice intact while replacing the least product-like part of the workflow: the user cannot yet manage an AI research team. Evidence ingestion and citation validation remain important, but they should be planned as trust infrastructure that supports desk work and thesis review.
