from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from studio_api.dependencies import get_store
from studio_api.storage import JsonStore
from studio_domain import ensure_pending_proposal
from studio_schemas import ActivityEvent, ActivityEventType, DecisionProposal, DecisionRequest, DecisionType, InvestmentDecision, ProposalStatus

router = APIRouter(prefix="/decision-proposals", tags=["decision-proposals"])
StoreDep = Annotated[JsonStore, Depends(get_store)]


@router.get("/{proposal_id}", response_model=DecisionProposal)
def get_proposal(proposal_id: str, store: StoreDep) -> DecisionProposal:
    return _get_proposal_or_404(store, proposal_id)


@router.post("/{proposal_id}/approve", response_model=InvestmentDecision)
def approve_proposal(proposal_id: str, request: DecisionRequest, store: StoreDep) -> InvestmentDecision:
    return _record_decision(store, proposal_id, DecisionType.APPROVED, ProposalStatus.APPROVED, request.user_note)


@router.post("/{proposal_id}/reject", response_model=InvestmentDecision)
def reject_proposal(proposal_id: str, request: DecisionRequest, store: StoreDep) -> InvestmentDecision:
    return _record_decision(store, proposal_id, DecisionType.REJECTED, ProposalStatus.REJECTED, request.user_note)


def _record_decision(store: JsonStore, proposal_id: str, decision: DecisionType, proposal_status: ProposalStatus, user_note: str | None) -> InvestmentDecision:
    proposal = _get_proposal_or_404(store, proposal_id)
    try:
        ensure_pending_proposal(proposal.status)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    investment_decision = InvestmentDecision(
        id=f"decision_{proposal.id}",
        project_id=proposal.project_id,
        proposal_id=proposal.id,
        thesis_id=proposal.thesis_id,
        decision=decision,
        user_note=user_note,
    )
    existing = store.get("decisions", investment_decision.id)
    if existing is not None:
        if existing.decision != decision:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="proposal already has a different decision")
        store.update("proposals", proposal.id, {"status": proposal_status})
        return existing

    investment_decision = store.create("decisions", investment_decision)
    proposal = store.update("proposals", proposal.id, {"status": proposal_status})
    store.create(
        "activity_events",
        ActivityEvent(
            project_id=proposal.project_id,
            event_type=ActivityEventType.DECISION_RECORDED,
            message=f"Recorded {decision.value} decision for {proposal.asset}.",
        ),
    )
    return investment_decision


def _get_proposal_or_404(store: JsonStore, proposal_id: str) -> DecisionProposal:
    proposal = store.get("proposals", proposal_id)
    if proposal is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision proposal not found.")
    return proposal
