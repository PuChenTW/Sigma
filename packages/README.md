# Packages

Shared product contracts and reusable internal packages live here.

Keep these packages free of app-framework concerns. They should define the domain language used by both apps and services.

## Directories

- `domain/`: Product domain model and lifecycle rules.
- `schemas/`: API, persistence, and agent IO schemas.
- `source-tools/`: Reusable source ingestion, transcript, ASR, and source-grounded LLM helper package.
