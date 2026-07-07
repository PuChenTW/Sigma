# Apps

User-facing application entrypoints live here.

These apps should depend on the Studio domain contracts and services, but product workflows should not be pushed down into `source_tools`.

## Directories

- `api/`: Backend API app. Intended runtime: FastAPI.
- `web/`: Frontend app. Intended runtime: Next.js.

