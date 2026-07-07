from fastapi import APIRouter, HTTPException, status

from studio_schemas import DecisionRequest

router = APIRouter(prefix="/decision-proposals", tags=["decision-proposals"])


def phase_3_not_ready() -> None:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Decision proposal endpoints are scheduled for MVP Phase 3.")


@router.get("/{proposal_id}")
def get_proposal(proposal_id: str) -> None:
    phase_3_not_ready()


@router.post("/{proposal_id}/approve", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def approve_proposal(proposal_id: str, request: DecisionRequest) -> None:
    phase_3_not_ready()


@router.post("/{proposal_id}/reject", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def reject_proposal(proposal_id: str, request: DecisionRequest) -> None:
    phase_3_not_ready()
