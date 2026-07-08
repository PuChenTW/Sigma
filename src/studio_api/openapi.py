from typing import Any

OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "Runtime health checks for local development, tests, and deployment probes.",
    },
    {
        "name": "research-projects",
        "description": "Create and inspect research projects, tasks, evidence, citations, artifacts, theses, proposals, and decisions.",
    },
    {
        "name": "committee",
        "description": "Evaluate a completed thesis through the Trading Committee boundary and create a bounded decision proposal.",
    },
    {
        "name": "decision-proposals",
        "description": "Inspect committee proposals and record the user's approve or reject decision.",
    },
]

NOT_FOUND_RESPONSE: dict[int, dict[str, Any]] = {
    404: {"description": "The requested project, thesis, proposal, or related record was not found."},
}

PROJECT_NOT_FOUND_RESPONSE: dict[int, dict[str, Any]] = {
    404: {"description": "The research project does not exist."},
}

PROPOSAL_NOT_FOUND_RESPONSE: dict[int, dict[str, Any]] = {
    404: {"description": "The decision proposal does not exist."},
}

CONFLICT_RESPONSE: dict[int, dict[str, Any]] = {
    409: {"description": "The request conflicts with the current project, proposal, workflow, or citation state."},
}
