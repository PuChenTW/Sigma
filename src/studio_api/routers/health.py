from fastapi import APIRouter

from studio_schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API health",
    description="Return a lightweight health response for local development, tests, and runtime probes.",
    response_description="API health status.",
)
def health() -> HealthResponse:
    return HealthResponse()
