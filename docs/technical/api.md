# API Design

FastAPI/OpenAPI is the source of truth for the current API surface.

Do not maintain a hand-written endpoint list in Markdown. Route paths, request/response schemas, summaries, descriptions, tags, and documented error responses should live in code and be generated through FastAPI.

## Runtime Docs

When the API is running:

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

Local development:

```bash
make api
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Code Locations

- App metadata and OpenAPI tag metadata: `src/studio_api/main.py`, `src/studio_api/openapi.py`
- Route metadata and handlers: `src/studio_api/routers/`
- Request and response schemas: `src/studio_schemas/`
- Domain transition rules: `src/studio_domain/`
- Workflow behavior: `src/studio_workflows/`

## Route Documentation Rules

Every public route should define:

- `tags` through its router.
- `summary` with a short user-facing action.
- `description` explaining when to use the route and what state it changes.
- `response_description` explaining the success response.
- `responses` for expected `404` and `409` cases when relevant.
- `response_model` so OpenAPI reflects the actual schema.

Descriptions should document product semantics, not implementation trivia. For example, approval routes should say that approval records an `InvestmentDecision` but does not execute a trade.

## Drift Prevention

Tests should inspect `/openapi.json` for route registration and metadata coverage. If a route is added without a useful summary or description, the API scaffold tests should fail.

Markdown may describe API design rules and where to find generated docs. It should not duplicate generated API reference content.
