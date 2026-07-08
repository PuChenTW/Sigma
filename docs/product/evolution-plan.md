# Product Evolution Plan

This document explains how to evolve from the current MVP toward the product north star in `docs/product/north-star.md`.

The prototype is a product reference for the desired Studio experience. It is not production architecture, not a data model, and not a promise that all visible screens should ship in one milestone.

## Why This Exists

`docs/product/status-and-roadmap.md` describes the current MVP vertical slice:

```text
Topic -> Research Project -> Evidence -> Thesis -> Decision Proposal -> User Decision
```

`frontend_prototype/` shows a richer operating system:

```text
Dashboard -> Research Team -> Research Library -> Decision Desk -> Positions -> Outcomes
```

Both are compatible, but the next product step should preserve the original product idea: the user manages an AI research team. The MVP proves one trust chain from topic to decision. The next phase should expose research desk ownership, task status, blockers, activity, and thesis challenge loops before expanding into a broad evidence-approval workflow.

The prototype intentionally looks like a complete investment command center. Implementation should translate that surface into durable lifecycle milestones:

```text
Research operations first
  -> thesis lifecycle
  -> decision queue
  -> manual / paper position outcome loop
  -> aggregate dashboard
```

Do not treat the prototype's visible portfolio metrics, active positions, or "approve and execute" language as permission to skip the research operating system or to create brokerage side effects. Those screens become real only when the underlying records exist.

## Product Capability Map

| Prototype capability | Product capability | Current state | Intended phase | Boundary to protect |
|---|---|---:|---:|---|
| Assign research task | Create research project and tasks from open-ended topic | MVP exists with fixed desks | P0/P1 | Research desk is a task template, not a runtime agent |
| Chief of Staff / CIO Router | Convert free-form topic into project objective and desk work | Not implemented | P1 | Router != autonomous decision maker |
| Research team status | Show task progress, blockers, dependencies, and activity | Minimal activity events | P1 | Role != runtime agent instance |
| Research report list | Browse durable theses and artifacts across projects | Project-local thesis view | P1/P2 | Report != Thesis |
| Thesis detail | Review thesis claims, evidence, risks, catalysts, invalidation | MVP thesis exists | P2 | Every claim needs citation lineage |
| Thesis challenge | Ask follow-ups, challenge assumptions, request more research | Not implemented | P2 | User challenge != investment decision |
| Decision desk | Review multiple committee proposals awaiting user action | Single proposal flow | P3 | Proposal != approved decision |
| Approve / reject proposal | Record durable user decision | MVP exists | P0/P3 | User keeps final control |
| Execute proposal | Record a user-entered execution intent or paper execution | Not implemented | P4 | Approval != brokerage trade |
| Active positions | Track approved thesis exposure and outcome | Explicitly out of MVP | P4 | Position tracking is downstream of decision quality |
| Position updates | Record current price, status, notes, partial exit | Not implemented | P4 | Market data can be manual before automated |
| Portfolio KPIs | Summarize exposure, PnL, active positions, pending decisions | Prototype only | P5 | Dashboard aggregates domain records; it does not own them |
| Multi-market workflow | Support equities, ETFs, commodities, FX, themes | Schemas are asset-oriented but MVP is SMR/OKLO | P3/P5 | Asset model should stay generic before adding asset-class features |

## Delivery Phases

### P0 - Trust Chain MVP

Goal: prove one complete, source-grounded path from topic to user decision.

Already covered by the current MVP:

- Free-form topic submission.
- Project, tasks, evidence, citations, artifacts, thesis, proposal, and decision.
- Backend evidence/citation contracts plus curated fallback evidence; the frontend shows citation traceability but no longer ships a standalone Evidence Workbench.
- Deterministic demo path without network or LLM dependencies.
- Playwright coverage for the primary flow.

Do not expand dashboards, portfolio state, or custom agents in P0.

### P1 - Research Team Workspace

Goal: make the product feel like managing an AI research team before it becomes a trading dashboard or data-labeling workflow.

Ship:

- Chief of Staff / CIO Router that turns a free-form topic into a project objective and desk-scoped tasks.
- Research team board with desks, task ownership, priority, status, blockers, dependencies, and activity.
- Project navigation and persisted project switching.
- Desk artifact summaries that show what each desk produced and what evidence or assumptions support it.
- Minimal thesis challenge/request-more-research action that creates follow-up desk work or records a challenge note.
- Deterministic planning and artifact generation as the testable baseline; no requirement for live agent orchestration yet.

The P1 UI may borrow the prototype's dashboard feel, but the first screen should center active research, team status, task queue, blockers, and pending user interventions. Portfolio KPIs and position P&L should remain absent or clearly mocked until P4/P5 records exist.

Exit criteria:

- A user can submit a broad research topic and see it become desk-level work without first choosing a ticker.
- A user can inspect which desks are queued, running, blocked, or done, and can drill into each desk's artifact.
- A user can challenge or request more research on a thesis and see the follow-up captured as durable project state.
- The existing committee proposal contract still works unchanged.

Defer:

- Portfolio dashboard.
- Position management.
- Execution reporting.
- Live autonomous source discovery.
- Broad source ingestion and document parsing.
- Per-excerpt evidence approval as a primary user workflow.
- A standalone Evidence Workbench separate from research assignment or thesis challenge workflows.
- Custom desk builder.

### P2 - Thesis Lifecycle And Evidence Traceability

Goal: make thesis review trustworthy and iterative once the user can already manage research work.

Ship:

- Thesis library across projects.
- Thesis detail with evidence, assumptions, catalysts, risks, and invalidation conditions.
- Thesis challenge/refinement workflow.
- URL/article and note/document source intake where the research workspace needs it, integrated into task intake or thesis challenge/refinement.
- Evidence review for cited excerpts and high-impact claims.
- Artifact and thesis generation grounded in project evidence or explicit assumptions.
- Optional additional fixed desks after repeated need is proven.

Exit criteria:

- A user can manage multiple research projects without losing lineage.
- Every thesis in the library links back to artifacts, citations, and project context.
- Challenge/refinement produces a new thesis version or explicit rejection reason.
- Generated artifacts and theses cannot cite missing, foreign, or unreviewed evidence where explicit review is required.

Defer:

- Active positions.
- PnL.
- Automated trading.
- Fully configurable workflows.

### P3 - Decision Desk

Goal: turn thesis review into a queue of bounded, auditable investment decisions.

Ship:

- Multiple pending `DecisionProposal` records.
- Proposal queue and proposal detail views.
- Proposal history and decision history.
- Proposal actions such as watch, approve, reject, defer, and request-more-research.
- Portfolio context input as a compact snapshot, not a full portfolio system.
- Optional TradingAgents integration behind the existing committee boundary.

Exit criteria:

- A user can compare pending proposals and resolve each one.
- Every proposal links to supporting thesis, artifacts, and citations.
- Rejection and request-more-research create useful feedback for future research.

Defer:

- Real execution.
- Position accounting.
- Broker integration.

### P4 - Position And Outcome Loop

Goal: close the loop from approved decision to monitored outcome without becoming an auto-trading platform.

Ship:

- `InvestmentPosition` or equivalent position record created only from an approved decision or explicit manual entry.
- Manual or paper execution details entered by the user: fill price, size, notes, status.
- Position update records: current price, partial exit, closed, thesis still valid or broken.
- Risk controls tied back to proposal: stop, target, sizing, invalidation.
- Outcome review linked to original thesis.

Exit criteria:

- A user can see whether an approved thesis is working, stale, invalidated, or closed.
- Position records remain traceable to the decision and thesis that created them.
- No brokerage side effects exist without a separate product decision.

Defer:

- Full portfolio accounting.
- Tax lots.
- Broker sync.
- Real-time market data dependency.

### P5 - Portfolio Dashboard

Goal: make the prototype dashboard real by aggregating durable records from earlier phases.

Ship:

- Dashboard KPIs derived from projects, proposals, decisions, and positions.
- Pending decision alerts.
- Active thesis and position summaries.
- Exposure and risk views once position data is reliable.
- Outcome feedback into research quality.

Exit criteria:

- Dashboard values can be traced to source records.
- No dashboard number is hand-maintained if the underlying domain record exists.
- Users can navigate from aggregate KPI to underlying thesis, proposal, decision, or position.

## Planning Rules

- Ship one capability axis at a time: research team workspace, thesis/evidence trust, decision queue, outcome loop, dashboard.
- A phase can start only when the previous phase has a working end-to-end path and tests.
- Do not introduce a new domain entity only for a screen. Add it when the product has a durable lifecycle to track.
- Keep deterministic fallbacks until the equivalent live/LLM path has contract tests.
- Use Playwright for every meaningful frontend workflow change.
- Keep `frontend_prototype/` as reference material. Production UI should reuse product concepts, not prototype runtime code.
- Do not promote TradingAgents integration ahead of P1/P2 just because the attached context discusses committee validation. TradingAgents is valuable after the Studio has research and thesis records worth sending to a committee.

## Recommended Next Milestone

The next milestone should be P1 Research Team Workspace:

```text
Free-form topic
  -> Chief of Staff / CIO Router
  -> desk-scoped research tasks
  -> team status / blockers / activity
  -> desk artifacts
  -> thesis challenge / request-more-research
  -> same committee proposal contract
```

This narrows the gap with the original product concept where the user operates an AI research team. Source ingestion and evidence approval remain important, but they should support thesis review and desk work rather than become the main user-facing milestone.
