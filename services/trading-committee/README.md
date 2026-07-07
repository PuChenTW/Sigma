# Trading Committee Service

Bounded investment decision workflow.

## Responsibility

- Accept compact thesis and research context.
- Evaluate one selected asset at a time for MVP.
- Produce a structured `DecisionProposal`.
- Keep committee workflow auditable.

## Boundary

TradingAgents may be used here, but its internal graph state must stay behind this boundary.

Do not pass the entire Evidence Store into committee state. Pass selected IDs, compact summaries, and explicit portfolio context.

