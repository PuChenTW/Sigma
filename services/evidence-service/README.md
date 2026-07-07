# Evidence Service

Evidence storage and retrieval boundary.

## Responsibility

- Persist `Evidence` records and source metadata.
- Support lookup by ID for citations.
- Support retrieval for research and committee context.
- Keep raw evidence separate from research artifacts.

## Future Direction

PostgreSQL full-text search, `pgvector`, and hybrid retrieval / RRF are the expected direction once persistence is implemented.

