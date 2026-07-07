from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from studio_api.routers import committee, decisions, health, projects

LOCAL_WEB_ORIGIN_REGEX = r"http://(localhost|127\.0\.0\.1):\d+"


def create_app() -> FastAPI:
    app = FastAPI(title="AI Investment Research Studio API", version="0.1.0")
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
