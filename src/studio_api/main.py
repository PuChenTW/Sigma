from fastapi import FastAPI

from studio_api.routers import committee, decisions, health, projects


def create_app() -> FastAPI:
    app = FastAPI(title="AI Investment Research Studio API", version="0.1.0")
    app.include_router(health.router)
    app.include_router(projects.router)
    app.include_router(committee.router)
    app.include_router(decisions.router)
    return app


app = create_app()
