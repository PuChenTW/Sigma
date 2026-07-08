# Product North Star

AI Investment Research Studio is an AI-assisted investment research operating system.

The user acts as a capital provider, investor, or CIO. They assign open-ended research topics, inspect AI research progress, review source-grounded theses, and decide whether research should be escalated into an investment decision.

This is not a stock chatbot, a single-ticker analyzer, an auto-trading bot, or a fixed multi-agent demo.

## Problem

Investors often start from broad questions, themes, events, or external sources rather than a ticker symbol.

Today that work is fragmented:

- Decomposing a topic into research tasks is manual.
- Sources, notes, and model outputs lose lineage quickly.
- AI-generated reports are hard to trust without citations.
- Reports do not naturally become durable investment theses.
- Investment recommendations often hide assumptions, risks, catalysts, and invalidation conditions.
- Approved decisions are hard to connect back to the thesis and evidence that justified them.
- The user needs final decision control, not automated trading.

The product should make investment research auditable from the first question through thesis formation, decision review, and outcome feedback.

## Product Promise

The Studio helps an investor operate an AI research team without giving up judgment or traceability.

The durable product loop is:

```text
Question / Topic / Source
  -> Research Project
  -> Research Tasks
  -> Evidence
  -> Research Artifacts
  -> Thesis
  -> Decision Proposal
  -> User Decision
  -> Position / Outcome Tracking
  -> Feedback Into Future Research
```

The product succeeds when the user can answer:

- What do we believe?
- Why do we believe it?
- Which evidence supports or weakens it?
- What decision is being proposed?
- What could invalidate the thesis?
- What happened after we approved, rejected, or deferred the decision?

## Target Users

Primary user:

- Capital provider, investor, or CIO who assigns research topics, reviews evidence-backed theses, and approves or rejects investment proposals.

Future secondary users:

- Research analyst reviewing, correcting, or challenging AI-generated work.
- Portfolio manager using approved theses and outcome history as investment decision inputs.

## North-Star Experience

The target experience is a workspace for investment research and decision operations.

`frontend_prototype/` is a useful reference for the intended product feel:

- A dashboard showing active research, pending proposals, active decisions, and portfolio/outcome summaries.
- A visible research team model with desks, focus areas, task status, blockers, and activity.
- A task assignment surface where the user can submit topics, attach sources, choose research facets, and set priority.
- A research library with projects, artifacts, theses, versions, challenges, and evidence trails.
- Thesis detail views with claims, confidence, evidence, key data, assumptions, risks, catalysts, invalidation conditions, and related decisions.
- A Decision Desk with bounded proposals, supporting thesis links, conviction, suggested sizing, risk controls, approve/reject/defer actions, and user feedback.
- A position and outcome workspace that tracks approved decisions, manual execution records, thesis validity, risk controls, updates, and post-decision results.

The prototype is not production architecture. It is the product direction reference.

## Product Capabilities

The final product should support these capability areas:

1. Research intake
   - Accept open-ended topics, questions, documents, URLs, notes, transcripts, and market context.
   - Preserve the user's intent and constraints before planning research.
2. Research planning
   - Convert intent into project-scoped tasks.
   - Assign tasks to concrete research desks such as Industry, Macro, Fundamental, Market Intelligence, Quant / Technical, and Narrative.
   - Track priority, status, blockers, and activity.
3. Evidence management
   - Ingest, extract, review, approve, and cite source material.
   - Keep raw evidence, citation excerpts, summaries, and inferences separate.
   - Make every claim traceable to approved evidence or an explicit assumption.
4. Thesis lifecycle
   - Turn artifacts into durable theses.
   - Support thesis versions, challenge/refinement workflows, confidence, assumptions, catalysts, risks, and invalidation conditions.
5. Decision workflow
   - Escalate selected theses into bounded decision proposals.
   - Preserve user final control through approve, reject, defer, and request-more-research actions.
   - Record decision rationale and feedback.
6. Outcome loop
   - Track approved decisions as paper/manual positions before any brokerage integration.
   - Record execution details, updates, thesis validity, risk controls, and outcomes.
   - Feed decision outcomes back into research quality.
7. Operating dashboard
   - Aggregate durable records into project, thesis, proposal, decision, position, risk, and outcome summaries.
   - Let users drill from every aggregate number back to the underlying source records.

## Product Boundaries

These boundaries define the product:

- `Research != InvestmentDecision`
- `Raw Evidence != ResearchArtifact`
- `Report != Thesis`
- `Decision Approval != Trade Execution`
- `Position Tracking != Portfolio Accounting`
- `Role != Runtime Agent Instance`
- `TradingAgents != Studio Domain Model`

The Studio may use agentic systems, LLMs, market data, and committee engines, but those systems serve the product workflow. They should not own the Studio's evidence, thesis, decision, or outcome history.

## Trust Principles

- Evidence comes before synthesis.
- Citations must resolve to project-owned evidence.
- Model output should distinguish evidence, inference, uncertainty, named entities, and numbers.
- The user keeps final decision authority.
- Dashboards summarize durable records; they do not invent state.
- Automation should be introduced only after the underlying manual workflow is clear and useful.

## Success Definition

At maturity, the product is working when:

- A user can manage multiple open-ended research projects without losing evidence lineage.
- A user can inspect why any thesis, proposal, decision, or position exists.
- Approved, rejected, deferred, and invalidated ideas all create reusable feedback.
- The product helps the user make better investment decisions without hiding uncertainty or automating away judgment.
