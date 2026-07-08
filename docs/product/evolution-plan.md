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

Both are compatible. The MVP proves the trust chain from topic to decision. The prototype shows the eventual workspace once there are enough projects, theses, proposals, and decisions to manage.

## Product Capability Map

| Prototype capability | Product capability | Current state | Intended phase | Boundary to protect |
|---|---|---:|---:|---|
| Assign research task | Create research project and tasks from open-ended topic | MVP exists with fixed desks | P0/P2 | Research desk is a task template, not a runtime agent |
| Research team status | Show task progress, blockers, and activity | Minimal activity events | P2 | Role != agent instance |
| Research report list | Browse durable theses and artifacts across projects | Project-local thesis view | P2 | Report != Thesis |
| Thesis detail | Review thesis claims, evidence, risks, catalysts, invalidation | MVP thesis exists | P1/P2 | Every claim needs citation lineage |
| Decision desk | Review multiple committee proposals awaiting user action | Single proposal flow | P3 | Proposal != approved decision |
| Approve / reject proposal | Record durable user decision | MVP exists | P0/P3 | User keeps final control |
| Execute proposal | Record an execution intent or paper execution | Not implemented | P4 | Approval != brokerage trade |
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
- Manual Evidence Workbench plus curated fallback evidence.
- Deterministic demo path without network or LLM dependencies.
- Playwright coverage for the primary flow.

Do not expand dashboards, portfolio state, or custom agents in P0.

### P1 - Real Evidence Loop

Goal: replace the least realistic part of the MVP without changing the decision boundary.

Ship:

- URL/article ingestion.
- Uploaded note or document ingestion.
- Evidence review queue where user-approved excerpts become citations.
- Artifact and thesis generation grounded only in approved citations.
- Deterministic fallback and tests for every generated path.

Exit criteria:

- A user can add at least one real source and see its approved citation used in a thesis.
- Generated artifacts cannot cite missing, foreign, or unapproved evidence.
- The existing committee proposal contract still works unchanged.

Defer:

- Portfolio dashboard.
- Position management.
- Autonomous source discovery.
- Custom desk builder.

### P2 - Research Workspace

Goal: make the product feel like a research operating system before it becomes a trading dashboard.

Ship:

- Project navigation and persisted project switching.
- Research task queue with priorities, statuses, blockers, and activity.
- Thesis library across projects.
- Thesis detail with evidence, assumptions, catalysts, risks, and invalidation conditions.
- Thesis challenge/refinement workflow.
- Optional additional fixed desks after repeated need is proven.

Exit criteria:

- A user can manage multiple research projects without losing lineage.
- Every thesis in the library links back to artifacts, citations, and project context.
- Challenge/refinement produces a new thesis version or explicit rejection reason.

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
- Manual execution details: fill price, size, notes, status.
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

- Ship one capability axis at a time: evidence, research workspace, decision queue, outcome loop, dashboard.
- A phase can start only when the previous phase has a working end-to-end path and tests.
- Do not introduce a new domain entity only for a screen. Add it when the product has a durable lifecycle to track.
- Keep deterministic fallbacks until the equivalent live/LLM path has contract tests.
- Use Playwright for every meaningful frontend workflow change.
- Keep `frontend_prototype/` as reference material. Production UI should reuse product concepts, not prototype runtime code.

## Recommended Next Milestone

The next milestone should be P1:

```text
Real evidence ingestion
  -> evidence review queue
  -> cited artifact generation
  -> thesis validation
  -> same committee proposal contract
  -> same decision UI path
```

This narrows the gap with the prototype where trust matters most: the user can rely on the research before the product adds more screens for decisions, positions, and dashboards.
