from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from studio_api.openapi import OPENAPI_TAGS
from studio_api.routers import committee, decisions, health, projects

LOCAL_WEB_ORIGIN_REGEX = r"http://(localhost|127\.0\.0\.1):\d+"


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Investment Research Studio API",
        summary="Source-grounded investment research workflow API.",
        description=(
            "API for the local Studio MVP: create research projects, attach cited evidence, "
            "run the deterministic demo workflow, evaluate a bounded committee proposal, "
            "and record the user's approve/reject decision. Research, evidence, thesis, "
            "proposal, and decision records remain separate so lineage is auditable."
        ),
        version="0.1.0",
        openapi_tags=OPENAPI_TAGS,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=LOCAL_WEB_ORIGIN_REGEX,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(projects.router)
    app.include_router(committee.router)
    app.include_router(decisions.router)
    return app


app = create_app()
