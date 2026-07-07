# MVP Product Spec

## 1. Executive Summary

AI Investment Research Studio MVP is a repeatable vertical slice that turns one free-form investment topic into a source-grounded thesis and a bounded investment decision proposal.

The MVP proves this workflow:

```text
Topic -> Research Project -> Research Tasks -> Evidence -> Research Artifacts -> Thesis -> Decision Proposal -> Investment Decision
```

The first demo path uses a small modular reactor (SMR) investment topic. The system creates a research project, runs fixed research desk tasks against curated evidence, produces cited artifacts, synthesizes one thesis, recommends one candidate asset, generates one committee proposal, and lets the user approve or reject it.

## 2. Background

The product is an AI-assisted investment research operating system. The intended user is a capital provider, investor, or CIO who manages research work rather than asking a one-off stock question.

Known repository facts:

- `src/studio_api` is the backend API boundary for project, workflow, committee, and decision endpoints.
- `src/studio_api`, `src/studio_domain`, `src/studio_schemas`, and `src/studio_workflows` contain the executable MVP backend foundation, deterministic research flow, and stubbed committee proposal flow.
- `frontend` contains the thin Next.js workflow UI and Playwright E2E demo path.
- Empty placeholder `packages/`, `services/`, and `vendor/` directories were removed; future modules should be added only when implementation needs them.
- `source_tools` is imported from `src/source_tools` during development. It provides reusable RSS, transcript, media, ASR wiring, and source-grounded LLM helpers without requiring a local wheel build.
- `frontend_prototype/投資工作室.dc.html` is a workflow/design reference, not production application architecture.
- Existing docs define TradingAgents as a future bounded Trading Committee engine, not the Studio domain model.

The MVP must preserve the product identity: topic-driven research first, investment decision second.

## 3. Problem Statement

Investors often start from broad investment questions rather than ticker symbols. Today they must manually decompose a topic into research tasks, gather sources, evaluate evidence, form a thesis, and translate that thesis into an investment decision.

The MVP should prove that AI Investment Research Studio can structure that process into an auditable workflow with visible task progress, source-backed artifacts, an inspectable thesis, and a bounded decision proposal.

## 4. Target Users

Primary user:

- Capital provider, investor, or CIO who assigns research topics, reviews evidence, and approves or rejects investment proposals.

Secondary future users:

- Research analyst reviewing or challenging AI-generated artifacts.
- Portfolio manager using approved theses as investment decision inputs.

Secondary users are not MVP design targets.

## 5. User Pain Points

- Investment questions start as themes, events, or sources, not always tickers.
- Research decomposition is manual and easy to lose track of.
- AI outputs are hard to trust without citations and evidence lineage.
- Reports do not naturally become versioned investment theses.
- Investment recommendations often lack visible assumptions, risks, catalysts, and invalidation conditions.
- A user needs decision control, not automated trading.

## 6. Product Goals

- Let a user submit a free-form investment topic without selecting a ticker first.
- Create a visible research project and fixed desk task plan.
- Preserve evidence and citation links through artifacts, thesis, and proposal rationale.
- Produce one inspectable thesis with support, counterpoints, assumptions, catalysts, invalidation conditions, horizon, and confidence.
- Escalate the thesis into one structured decision proposal for a selected candidate asset.
- Record the user's approve or reject decision.
- Keep the MVP reliable and repeatable for demo.

## 7. Non-Goals

- Automated trade execution.
- Brokerage integration.
- Full portfolio accounting.
- Full position lifecycle management.
- Multi-user collaboration.
- Production-grade authentication or permissions.
- General-purpose web crawling or open-ended source discovery.
- Deep TradingAgents integration.
- Autonomous multi-agent orchestration.
- Custom research desks or workflow builder.
- Multiple competing theses per project.
- Market data platform.
- Analyst scoring or advanced source reliability scoring.
- Feedback analytics.
- Event sourcing.
- Production observability stack.

## 8. Core Product Hypothesis

This MVP validates:

> If a user can submit one free-form investment topic and receive a persisted, cited thesis plus a bounded approve/reject decision proposal, they will understand the product as an investment research operating system rather than a chatbot or single-ticker report generator.

The MVP focuses on workflow credibility, traceability, and decision readiness. It does not attempt to prove broad autonomous research, live market integration, or trading execution.

## 9. Primary User Journey

1. User opens the Studio dashboard-lite view.
2. User submits a free-form topic: "Are small modular reactors becoming an investable theme, and which public company is the best first candidate?"
3. System creates a `ResearchProject`.
4. System creates fixed `ResearchTask` records for:
   - Industry
   - Macro/Policy
   - Fundamental/company candidate
5. User sees task status and basic activity events.
6. System attaches curated evidence to the project and tasks.
7. Each task produces a cited `ResearchArtifact`.
8. System synthesizes one `Thesis`.
9. Thesis detail shows the claim, evidence for, risks/counterpoints, assumptions, catalysts, invalidation conditions, horizon, confidence, and candidate asset rationale.
10. System sends the thesis and compact context to the Trading Committee boundary.
11. Stubbed committee returns one `DecisionProposal`.
12. User reviews action, asset, rationale, sizing guidance, risk controls, and supporting thesis links.
13. User approves or rejects the proposal.
14. System records an `InvestmentDecision` linked back to the proposal, thesis, artifacts, and citations.

## 10. MVP Scope

### Must Have

- Free-form topic submission.
- Persisted research project.
- Fixed three-desk task plan for Industry, Macro/Policy, and Fundamental/company candidate research.
- Simple task statuses: `pending`, `running`, `done`, `failed`, `blocked`.
- Minimal timestamped activity timeline.
- Curated SMR evidence set.
- Evidence metadata and citation IDs.
- Cited research artifacts.
- One synthesized thesis.
- One traceable candidate asset recommendation.
- Trading Committee interface with stub implementation.
- One structured decision proposal.
- Approve/reject action.
- Persisted investment decision.
- Thin frontend screens for project list/dashboard-lite, assign topic, project detail, thesis detail, and proposal review.
- Basic API and domain schema contracts.
- End-to-end demo path that works without live network or LLM dependencies.

### Should Have

- Optional schema-validated LLM synthesis for artifacts and thesis.
- Deterministic seeded fallback for every generated artifact and proposal.
- Basic error display when a workflow step fails.
- Citation links visible in thesis and proposal screens.
- API/domain support for multiple projects, even if the demo UI centers one active project.

### Explicitly Deferred

- Real TradingAgents integration.
- Arbitrary URL crawling and source discovery.
- PDFs, screenshots, and broad media ingestion unless already available as curated text.
- Candidate asset override, unless cheap after core flow works.
- Portfolio/position state changes after approval.
- Production authentication.
- Background jobs and durable orchestration.
- Market data and price charts.
- Multi-thesis comparison.
- Analyst/source scoring.
- Deployment hardening.

## 11. Functional Requirements

### FR-001 - Submit Free-Form Research Topic

- Description: The user can submit a plain-language investment topic without selecting a ticker.
- User Value: Preserves topic-driven research behavior.
- Priority: Must Have
- Acceptance Criteria:
  - User can enter and submit a topic from the UI.
  - API accepts a topic string and creates a project.
  - Empty topics are rejected with a visible error.

### FR-002 - Create Research Project

- Description: The system creates a persisted `ResearchProject` with title, topic, objective, status, and timestamps.
- User Value: Gives the research workflow a durable root object.
- Priority: Must Have
- Acceptance Criteria:
  - A submitted topic creates exactly one project.
  - Project can be retrieved after page refresh or API restart within the chosen persistence mode.
  - Project status is visible in UI.

### FR-003 - Create Fixed Research Tasks

- Description: The system creates fixed desk tasks for Industry, Macro/Policy, and Fundamental/company candidate research.
- User Value: Shows the topic being decomposed into research work.
- Priority: Must Have
- Acceptance Criteria:
  - Each new project creates the three required tasks.
  - Each task has a desk, title, status, and project link.
  - No custom desks are required in MVP.

### FR-004 - Track Task Status And Activity

- Description: The user can see task statuses and minimal timestamped activity events.
- User Value: Makes the product feel like a research operating system rather than a black-box generator.
- Priority: Must Have
- Acceptance Criteria:
  - Tasks can show `pending`, `running`, `done`, `failed`, or `blocked`.
  - Project detail shows current status for each task.
  - Activity events show meaningful workflow steps, not fake agent activity.

### FR-005 - Attach Evidence With Citations

- Description: The system stores curated evidence records and citation IDs used by artifacts, thesis, and proposal.
- User Value: Allows the user to inspect why a claim exists.
- Priority: Must Have
- Acceptance Criteria:
  - Evidence records include source title, source type, URL or fixture reference, content excerpt or summary, and metadata.
  - Citation IDs are stable and linked to evidence records.
  - At least one citation is attached to each completed artifact.

### FR-006 - Generate Cited Research Artifacts

- Description: Each desk produces a text artifact with findings, citations, risks, and uncertainty notes.
- User Value: Provides intermediate research outputs the user can inspect.
- Priority: Must Have
- Acceptance Criteria:
  - Industry, Macro/Policy, and Fundamental tasks each produce one artifact.
  - Artifact citations resolve to evidence records.
  - Artifacts distinguish findings from risks or uncertainty.

### FR-007 - Synthesize Thesis

- Description: The system synthesizes one thesis from artifacts and evidence.
- User Value: Converts research outputs into an investment thesis.
- Priority: Must Have
- Acceptance Criteria:
  - Thesis includes claim, evidence for, counter-evidence or risks, assumptions, catalysts, invalidation conditions, horizon, confidence, and status.
  - Thesis links to source artifacts and evidence citations.
  - Thesis can be opened from the project detail screen.

### FR-008 - Recommend One Candidate Asset

- Description: The thesis includes one candidate asset recommendation with traceable rationale.
- User Value: Bridges topic research to a bounded investment decision.
- Priority: Must Have
- Acceptance Criteria:
  - Candidate asset is stored on the thesis or proposal input.
  - Rationale references artifacts or citations.
  - The demo path uses exactly one candidate asset for committee review.

### FR-009 - Generate Decision Proposal

- Description: The Trading Committee boundary returns one structured proposal from thesis context.
- User Value: Turns a thesis into a decision-ready object while preserving user control.
- Priority: Must Have
- Acceptance Criteria:
  - Proposal includes asset, action, conviction, horizon, sizing guidance, entry conditions, invalidation or stop conditions, primary risks, rationale, and supporting thesis ID.
  - Proposal is generated through a committee interface or endpoint.
  - Proposal links back to thesis and citations.

### FR-010 - Review Proposal

- Description: User can inspect the proposal before deciding.
- User Value: Keeps the user as final decision maker.
- Priority: Must Have
- Acceptance Criteria:
  - Proposal detail screen shows action, asset, rationale, risks, sizing guidance, and supporting thesis references.
  - Proposal status is visible.
  - User can navigate back to the thesis context.

### FR-011 - Approve Or Reject Proposal

- Description: User can approve or reject a proposal.
- User Value: Completes the bounded decision loop without executing trades.
- Priority: Must Have
- Acceptance Criteria:
  - User can approve a pending proposal.
  - User can reject a pending proposal.
  - Approved/rejected proposals cannot be decided again without explicit reset not included in MVP.

### FR-012 - Record Investment Decision

- Description: The system persists an `InvestmentDecision` linked to proposal, thesis, project, and user action.
- User Value: Creates an auditable record of the final decision.
- Priority: Must Have
- Acceptance Criteria:
  - Approve/reject creates one decision record.
  - Decision stores status, rationale or user note if provided, timestamps, proposal ID, and thesis ID.
  - Approval does not create a trade or position.

### FR-013 - Provide Repeatable Demo Fallback

- Description: The complete SMR flow works using seeded evidence and deterministic generated outputs.
- User Value: Ensures the MVP can be shown reliably.
- Priority: Must Have
- Acceptance Criteria:
  - Demo can run without live network calls.
  - Demo can run without external LLM calls.
  - Seeded outputs still preserve citation links.

## 12. Non-Functional Expectations

- Reliability: The canonical demo path must complete deterministically.
- Persistence: Created projects, artifacts, thesis, proposal, and decision must survive a page refresh and basic backend restart in the chosen MVP persistence mode.
- Traceability: Every artifact, thesis, and proposal rationale must retain citation links.
- Latency: Seeded/demo workflow should complete within a few seconds after submission on a local development machine.
- Security: No brokerage credentials or trading execution credentials are handled in MVP.
- Observability: Basic structured logs and visible failed task states are sufficient.
- Testability: Domain transitions, citation links, and approve/reject behavior must be testable without network or LLM calls.

## 13. Edge Cases

- Empty topic submission.
- Unsupported or non-demo topic submitted before generalized research exists.
- Evidence fixture missing or malformed.
- Generated artifact lacks citations.
- Thesis synthesis fails validation.
- Committee proposal generation fails.
- User tries to approve or reject an already decided proposal.
- User refreshes while workflow status is mid-transition.
- One task fails while other tasks complete.

## 14. Demo Scenario

### Preconditions

- The MVP app is running locally.
- The SMR evidence fixture bundle is available.
- The deterministic workflow runner is enabled.
- Optional LLM generation is disabled or has deterministic fallback.

### Demo Steps

1. Open the Studio UI.
2. Submit: "Are small modular reactors becoming an investable theme, and which public company is the best first candidate?"
3. Open the created research project.
4. Observe Industry, Macro/Policy, and Fundamental tasks.
5. Run or observe task completion.
6. Open each cited research artifact.
7. Open the synthesized thesis.
8. Inspect claim, evidence, risks, assumptions, catalysts, invalidation conditions, horizon, confidence, and candidate asset.
9. Open the committee decision proposal.
10. Review action, asset, conviction, sizing guidance, risks, and rationale.
11. Approve or reject the proposal.
12. Confirm the decision record appears with links back to proposal, thesis, artifacts, and citations.

### Expected Result

The user sees a complete, persisted, auditable path from topic to investment decision. The output demonstrates research workflow, citation traceability, thesis structure, and decision control.

### Failure Cases

- If evidence is missing, task status becomes `failed` or `blocked` with an explanation.
- If artifact or thesis validation fails, the project shows a failed workflow step.
- If proposal generation fails, the thesis remains visible and the proposal state shows failure.
- If a user retries approve/reject on a decided proposal, the UI and API reject it.

## 15. Success Criteria

- A user can complete the full SMR demo through the UI.
- All Must Have functional requirements pass acceptance criteria.
- Every thesis and proposal claim shown in the demo has citation lineage.
- Approve/reject creates a durable decision record.
- The demo works without live network or LLM dependencies.
- Playwright verifies the primary user workflow.
- The MVP does not require production auth, TradingAgents integration, market data, or portfolio accounting.

## 16. Assumptions

- One strong SMR demo scenario is enough to validate product identity.
- Workflow value matters more than broad source coverage in the MVP.
- The first research desks are templates and labels, not autonomous runtime agents.
- Stubbed committee output is acceptable if the interface and proposal contract are real.
- Local persistence is acceptable if schemas remain compatible with future PostgreSQL.
- `source_tools` remains product-agnostic and reusable.

## 17. Open Questions

- Should MVP persistence use SQLite or JSON-backed local storage?
- Which curated SMR evidence sources should be frozen for the canonical demo?
- Should optional LLM synthesis ship enabled by default or behind a configuration flag?
- Should proposal actions include only `watch`, `buy`, `avoid`, or a broader vocabulary?
- Should candidate asset override be included if it is cheap after core flow works?

## 18. Future Extensions

- Real TradingAgents integration behind the committee boundary.
- PostgreSQL with full-text search, `pgvector`, and hybrid retrieval.
- Additional source ingestion: PDFs, uploaded files, YouTube, podcasts, transcripts, and notes.
- Configurable research desks.
- Multi-thesis comparison and thesis version diff UI.
- Portfolio and position lifecycle.
- Market data integration.
- Background jobs and durable orchestration.
- Multi-user collaboration and permissions.
- Observability with Langfuse and OpenTelemetry.
- Feedback loop from decisions and outcomes into future research quality.
