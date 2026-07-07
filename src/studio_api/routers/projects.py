from fastapi import APIRouter, HTTPException, status

from studio_schemas import CreateResearchProjectRequest

router = APIRouter(prefix="/research-projects", tags=["research-projects"])


def phase_2_not_ready() -> None:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Project workflow endpoints are scheduled for MVP Phase 2.")


@router.post("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def create_project(_: CreateResearchProjectRequest) -> None:
    phase_2_not_ready()


@router.get("")
def list_projects() -> None:
    phase_2_not_ready()


@router.get("/{project_id}")
def get_project(project_id: str) -> None:
    phase_2_not_ready()


@router.get("/{project_id}/tasks")
def list_project_tasks(project_id: str) -> None:
    phase_2_not_ready()


@router.get("/{project_id}/artifacts")
def list_project_artifacts(project_id: str) -> None:
    phase_2_not_ready()


@router.get("/{project_id}/thesis")
def get_project_thesis(project_id: str) -> None:
    phase_2_not_ready()
