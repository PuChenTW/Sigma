# API App

Backend API for AI Investment Research Studio.

## Responsibility

- Expose product APIs for projects, tasks, evidence, artifacts, theses, decision proposals, and decisions.
- Coordinate service calls without embedding long-running agent workflow logic directly in route handlers.
- Provide streaming or polling endpoints for activity status when the event model exists.

## Not Responsibility

- Do not implement reusable ingestion primitives here; use `source_tools` or `services/ingestion`.
- Do not expose TradingAgents internals as public API.
- Do not store hidden app settings inside `source_tools`.

## First MVP APIs

- `POST /research-projects`
- `GET /research-projects`
- `GET /research-projects/{project_id}`
- `POST /research-projects/{project_id}/tasks`
- `POST /evidence`
- `POST /research-projects/{project_id}/theses`
- `POST /committee/evaluate`
- `POST /decision-proposals/{proposal_id}/approve`
- `POST /decision-proposals/{proposal_id}/reject`

