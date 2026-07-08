# Product

AI Investment Research Studio is an AI-assisted investment research operating system.

The user acts as a capital provider, investor, or CIO. They assign open-ended research topics, inspect research progress, review source-grounded theses, and decide whether a thesis should become an investment decision.

This is not a stock chatbot, a single-ticker analyzer, an auto-trading bot, or a fixed multi-agent demo.

## Problem

Investors often start from broad questions, themes, events, or external sources rather than a ticker symbol.

Today that work is fragmented:

- Decomposing a topic into research tasks is manual.
- Sources, notes, and model outputs lose lineage quickly.
- AI-generated reports are hard to trust without citations.
- Reports do not naturally become durable investment theses.
- Investment recommendations often hide assumptions, risks, catalysts, and invalidation conditions.
- The user needs final decision control, not automated trading.

The product should make research work auditable from the first question to the final approve/reject decision.

## Goal

The core goal is to prove this workflow:

```text
Topic
  -> Research Project
  -> Research Tasks
  -> Evidence
  -> Research Artifacts
  -> Thesis
  -> Trading Committee
  -> Decision Proposal
  -> User Approve / Reject
```

The MVP succeeds when a user can submit one free-form investment topic and receive a persisted, cited thesis plus a bounded decision proposal they can approve or reject.

The first demo path uses small modular reactors (SMR) as the canonical topic.

## Target User

Primary user:

- Capital provider, investor, or CIO who assigns research topics, reviews evidence, and approves or rejects investment proposals.

Future secondary users:

- Research analyst reviewing or challenging AI-generated artifacts.
- Portfolio manager using approved theses as investment decision inputs.

Secondary users are not the MVP design target.

## Product Model

The product should help the user manage a research team:

1. Submit a free-form topic or external source without choosing a ticker first.
2. Let a CIO / Chief of Staff layer interpret intent, create a research project, and plan tasks.
3. Assign work to research desks such as Industry, Macro, Fundamental, Market Intelligence, Quant / Technical, and Narrative.
4. Track research tasks, status, blockers, and activity.
5. Preserve evidence from media, articles, transcripts, PDFs, notes, market data, and other sources.
6. Produce research artifacts and evolve them into versioned investment theses.
7. Escalate selected theses and assets into a Trading Committee for a bounded investment decision.
8. Track decisions, positions, outcomes, and feedback over time.

## MVP Scope

The MVP should stay narrow and repeatable.

Must have:

- Free-form topic submission.
- Persisted research project.
- Fixed three-desk task plan:
  - Industry
  - Macro / Policy
  - Fundamental / company candidate
- Task statuses and minimal activity timeline.
- Curated SMR evidence set.
- Evidence metadata and stable citation IDs.
- One cited research artifact per desk.
- One synthesized thesis.
- One traceable candidate asset recommendation.
- Trading Committee interface with a stub implementation.
- One structured decision proposal.
- Approve/reject action.
- Persisted investment decision.
- Thin UI for topic submission, project review, thesis/proposal review, and decision.
- End-to-end demo path that works without live network or LLM dependencies.

Should have:

- Deterministic fallback for every generated artifact and proposal.
- Basic error display when a workflow step fails.
- Citation links visible in thesis and proposal views.
- API/domain support for multiple projects, even if the demo UI centers one active project.

## Out Of Scope

Do not include in the first MVP:

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

## Functional Design

Primary user journey:

1. User opens the Studio workflow UI.
2. User submits a topic such as:

   ```text
   Are small modular reactors becoming an investable theme, and which public company is the best first candidate?
   ```

3. System creates a `ResearchProject`.
4. System creates fixed `ResearchTask` records for Industry, Macro/Policy, and Fundamental research.
5. User sees task status and meaningful activity events.
6. System attaches curated evidence to the project and tasks.
7. Each task produces a cited `ResearchArtifact`.
8. System synthesizes one `Thesis`.
9. Thesis detail shows the claim, evidence for, risks, assumptions, catalysts, invalidation conditions, horizon, confidence, and candidate asset rationale.
10. System sends compact thesis context to the Trading Committee boundary.
11. Committee returns one `DecisionProposal`.
12. User reviews action, asset, conviction, sizing guidance, risk controls, rationale, and supporting thesis links.
13. User approves or rejects the proposal.
14. System records an `InvestmentDecision` linked back to the proposal, thesis, artifacts, and citations.

## Success Criteria

- A user can complete the full SMR demo through the UI.
- The demo works without live network or LLM dependencies.
- Every thesis and proposal claim shown in the demo has citation lineage.
- Approve/reject creates a durable decision record.
- Playwright verifies the primary user workflow.
- The MVP does not require production auth, TradingAgents integration, market data, or portfolio accounting.

## Future Product Directions

After the MVP works, the most useful product directions are:

- Real source ingestion from URLs, RSS, transcripts, PDFs, uploaded notes, and market data.
- Optional schema-validated LLM synthesis behind deterministic fallbacks.
- Thesis versioning, comparison, and challenge workflows.
- Configurable research desks after fixed desks prove useful.
- Real TradingAgents integration behind the committee boundary.
- Position and outcome tracking after user-approved decisions.
- Feedback loops from decisions and outcomes into future research quality.
