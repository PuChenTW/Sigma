# Services

Longer-running product capabilities live here.

Services can begin as in-process modules called by `apps/api`. Split them into separate processes only when deployment, scaling, or reliability requires it.

## Directories

- `ingestion/`: Evidence ingestion and normalization.
- `research-orchestrator/`: Topic interpretation, task planning, and research execution coordination.
- `evidence-service/`: Evidence storage and retrieval boundary.
- `thesis-registry/`: Thesis lifecycle and versioning boundary.
- `trading-committee/`: Bounded wrapper around TradingAgents or equivalent committee workflow.

