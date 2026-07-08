# Product North Star

AI Investment Research Studio is an AI-assisted investment research operating system.

The user acts as a capital provider, investor, or CIO. They assign open-ended research topics and outside material to an AI research team, inspect what each research desk is doing, question or challenge the work, review durable theses, and decide whether a thesis should be escalated into an investment decision.

This is not a stock chatbot, a single-ticker analyzer, an auto-trading bot, or a fixed multi-agent demo.

## Problem

Investors often start from broad questions, themes, events, or external sources rather than a ticker symbol.

Today that work is fragmented:

- Turning a broad topic into desk-level research work is manual.
- It is hard to see which analyst or desk is working on what, what is blocked, and what has already been produced.
- Sources, notes, and model outputs lose lineage quickly.
- AI-generated reports are hard to trust without citations.
- Reports do not naturally become durable investment theses.
- Users cannot naturally ask follow-up questions, challenge a thesis, or send the work back for more research.
- Investment recommendations often hide assumptions, risks, catalysts, and invalidation conditions.
- Approved decisions are hard to connect back to the thesis and evidence that justified them.
- The user needs final decision control, not automated trading.

The product should make investment research auditable from the first question through thesis formation, decision review, and outcome feedback.

## Product Promise

The Studio helps an investor operate an AI research team without giving up judgment or traceability.

The durable product loop is:

```text
Question / Topic / Source / Media
  -> Chief of Staff / CIO Router
  -> Research Project
  -> Research Desk Tasks
  -> Desk Activity / Blockers / Outputs
  -> Evidence Store + Research Memory
  -> Research Artifacts
  -> Thesis Registry
  -> Challenge / Refinement
  -> Trading Committee Proposal
  -> User Decision
  -> Position / Outcome Tracking
  -> Feedback Into Future Research
```

The product succeeds when the user can answer:

- What is the research team working on?
- Which desk owns this question, and what is blocked?
- What do we believe?
- Why do we believe it?
- Which evidence supports or weakens it?
- What did I challenge, and how did the thesis change?
- What decision is being proposed?
- What could invalidate the thesis?
- What happened after we approved, rejected, or deferred the decision?

## Target Users

Primary user:

- Capital provider, investor, or CIO who assigns research topics and outside material to an AI research team, monitors progress, challenges the work, reviews evidence-backed theses, and approves, rejects, or defers investment proposals.

Future secondary users:

- Research analyst reviewing, correcting, or challenging AI-generated work.
- Portfolio manager using approved theses and outcome history as investment decision inputs.

## North-Star Experience

The target experience is a workspace for investment research and decision operations.

`frontend_prototype/` is a useful reference for the intended product feel:

- A dashboard showing active research, pending proposals, active decisions, and portfolio/outcome summaries.
- A visible research team model with desks, focus areas, task status, blockers, and activity.
- A task assignment surface where the user can submit topics, attach sources, choose research facets, and set priority.
- A Chief of Staff / CIO Router that turns free-form topics into project-scoped research tasks and activates the relevant desks.
- A research library with projects, artifacts, theses, versions, challenges, and evidence trails.
- Thesis detail views with claims, confidence, evidence, key data, assumptions, risks, catalysts, invalidation conditions, and related decisions.
- A Decision Desk with bounded proposals, supporting thesis links, conviction, suggested sizing, risk controls, approve/reject/defer actions, and user feedback.
- A position and outcome workspace that tracks approved decisions, manual execution records, thesis validity, risk controls, updates, and post-decision results.

The prototype is not production architecture. It is the product direction reference.

### Prototype Interpretation

The prototype should be read as the mature Studio operating surface, not as the next implementation milestone and not as a trading-first mandate.

Its dashboard, Decision Desk, positions, and execution reporting screens are downstream of the research operating system:

- The first product gap to close is still the user's ability to assign broad research topics, see desk ownership, inspect blockers, and challenge theses.
- Decision proposals become useful only after they are traceably linked to theses, artifacts, and evidence.
- "Approve and execute" in the prototype maps to user-controlled approval plus a manual or paper execution record. It must not imply brokerage execution or automated trading.
- Position and portfolio views summarize approved decisions and later manual outcome records. They do not replace the research, thesis, and decision lifecycle.
- The prototype's four research facets are a simplified UI grouping. The domain should continue to support concrete desks such as Industry, Macro, Fundamental, Market Intelligence, Quant / Technical, and Narrative when the work requires them.

## Product Capabilities

The final product should support these capability areas:

1. Research intake
   - Accept open-ended topics, questions, documents, URLs, notes, transcripts, media, screenshots, interviews, earnings calls, and market context.
   - Preserve the user's intent and constraints before planning research.
2. Research planning
   - Convert intent into project-scoped tasks through a Chief of Staff / CIO Router.
   - Assign tasks to concrete research desks such as Industry, Macro, Fundamental, Market Intelligence, Quant / Technical, and Narrative.
   - Support task dependencies, priority, status, blockers, retries, user interruption, and activity history.
3. Research team operations
   - Show what each desk is working on, waiting for, and producing.
   - Let the user ask follow-up questions, redirect research, or challenge a thesis.
   - Treat desks as product roles and task templates, not necessarily one runtime agent per role.
4. Evidence management
   - Ingest, extract, review, and cite source material.
   - Keep raw evidence, citation excerpts, summaries, and inferences separate.
   - Make every claim traceable to approved evidence or an explicit assumption.
   - Use evidence review as a trust gate for cited claims and high-impact excerpts, not as the primary user job of approving every document line-by-line.
5. Thesis lifecycle
   - Turn artifacts into durable theses.
   - Support thesis versions, challenge/refinement workflows, confidence, assumptions, catalysts, risks, and invalidation conditions.
6. Trading Committee / decision workflow
   - Escalate selected theses into bounded decision proposals.
   - Use TradingAgents or another bounded committee engine behind the Studio domain boundary.
   - Preserve user final control through approve, reject, defer, and request-more-research actions.
   - Record decision rationale and feedback.
7. Outcome loop
   - Track approved decisions as paper/manual positions before any brokerage integration.
   - Record execution details, updates, thesis validity, risk controls, and outcomes.
   - Feed decision outcomes back into research quality.
8. Operating dashboard
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
- `Research Desk != TradingAgents Analyst`
- `TradingAgents != Studio Domain Model`

The Studio may use agentic systems, LLMs, market data, and committee engines, but those systems serve the product workflow. They should not own the Studio's evidence, thesis, decision, or outcome history.

## Trust Principles

- Evidence comes before synthesis.
- Citations must resolve to project-owned evidence.
- Model output should distinguish evidence, inference, uncertainty, named entities, and numbers.
- The user reviews research and thesis quality; the product should not turn the user into a line-by-line data-labeling operator.
- The user keeps final decision authority.
- Dashboards summarize durable records; they do not invent state.
- Automation should be introduced only after the underlying manual workflow is clear and useful.

## Success Definition

At maturity, the product is working when:

- A user can manage multiple open-ended research projects without losing evidence lineage.
- A user can see and steer the AI research team's work across desks, tasks, blockers, and artifacts.
- A user can inspect why any thesis, proposal, decision, or position exists.
- Approved, rejected, deferred, and invalidated ideas all create reusable feedback.
- The product helps the user make better investment decisions without hiding uncertainty or automating away judgment.
