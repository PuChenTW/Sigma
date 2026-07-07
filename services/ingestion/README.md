# Ingestion Service

Evidence ingestion and normalization boundary.

## Responsibility

- Accept URLs, RSS items, transcripts, and manual notes.
- Use `source_tools` for reusable RSS/media/transcript capabilities.
- Normalize raw source content into `Evidence` records.
- Preserve source metadata and provenance.

## Not Responsibility

- Do not generate investment theses here.
- Do not make trading recommendations here.
- Do not hide API keys or app settings inside `source_tools`.

