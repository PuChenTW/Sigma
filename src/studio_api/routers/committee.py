from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/research-projects/{project_id}/committee", tags=["committee"])


@router.post("/evaluate", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def evaluate_project(project_id: str) -> None:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Committee evaluation is scheduled for MVP Phase 3.")
