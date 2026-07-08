from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from studio_api.dependencies import get_store
from studio_api.openapi import CONFLICT_RESPONSE, PROJECT_NOT_FOUND_RESPONSE
from studio_api.storage import JsonStore
from studio_domain import ensure_project_citations_resolve
from studio_schemas import ActivityEvent, ActivityEventType, DecisionProposal, Evidence, ResearchProject, Thesis
from studio_workflows import evaluate_committee

router = APIRouter(prefix="/research-projects/{project_id}/committee", tags=["committee"])
StoreDep = Annotated[JsonStore, Depends(get_store)]


@router.post(
    "/evaluate",
    response_model=DecisionProposal,
    summary="Evaluate project thesis",
    description=(
        "Send the latest project thesis through the Trading Committee boundary and create a bounded decision proposal. "
        "The committee receives compact research context; it does not own research projects, evidence, or thesis lifecycle."
    ),
    response_description="The created or existing decision proposal for the latest thesis.",
    responses={**PROJECT_NOT_FOUND_RESPONSE, **CONFLICT_RESPONSE},
)
def evaluate_project(project_id: str, store: StoreDep) -> DecisionProposal:
    project = _get_project_or_404(store, project_id)
    thesis = _get_project_thesis_or_409(store, project.id)

    try:
        proposal = evaluate_committee(project, thesis)
        ensure_project_citations_resolve(project.id, proposal.citation_ids, _project_evidence(store, project.id), store.list("citations"))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    existing = store.get("proposals", proposal.id)
    if existing is not None:
        return existing

    proposal = store.create("proposals", proposal)
    store.create(
        "activity_events",
        ActivityEvent(project_id=project.id, event_type=ActivityEventType.PROPOSAL_CREATED, message=f"Created committee proposal for {proposal.asset}."),
    )
    return proposal


def _get_project_or_404(store: JsonStore, project_id: str) -> ResearchProject:
    project = store.get("projects", project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return project


def _get_project_thesis_or_409(store: JsonStore, project_id: str) -> Thesis:
    theses = [thesis for thesis in store.list("theses") if thesis.project_id == project_id]
    if not theses:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Project has no thesis. Run the demo workflow first.")
    return sorted(theses, key=lambda thesis: thesis.version)[-1]


def _project_evidence(store: JsonStore, project_id: str) -> list[Evidence]:
    return [item for item in store.list("evidence") if item.project_id == project_id]
