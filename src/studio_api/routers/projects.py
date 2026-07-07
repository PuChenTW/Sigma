from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from studio_api.dependencies import get_store
from studio_api.storage import JsonStore
from studio_schemas import (
    ActivityEvent,
    ActivityEventType,
    CreateResearchProjectRequest,
    DecisionProposal,
    DemoWorkflowResponse,
    Evidence,
    EvidenceCitation,
    InvestmentDecision,
    ProjectStatus,
    ResearchArtifact,
    ResearchProject,
    ResearchTask,
    Thesis,
)
from studio_workflows import WorkflowError, plan_tasks, run_demo_workflow

router = APIRouter(prefix="/research-projects", tags=["research-projects"])
StoreDep = Annotated[JsonStore, Depends(get_store)]


def project_title(topic: str) -> str:
    topic = topic.strip()
    if len(topic) <= 72:
        return topic
    return f"{topic[:69].rstrip()}..."


@router.post("", response_model=ResearchProject, status_code=status.HTTP_201_CREATED)
def create_project(request: CreateResearchProjectRequest, store: StoreDep) -> ResearchProject:
    project = store.create(
        "projects",
        ResearchProject(
            title=project_title(request.topic),
            topic=request.topic,
            objective=f"Assess investable implications of: {request.topic}",
            status=ProjectStatus.CREATED,
        ),
    )
    store.create(
        "activity_events",
        ActivityEvent(project_id=project.id, event_type=ActivityEventType.PROJECT_CREATED, message="Created research project."),
    )
    for task in plan_tasks(project):
        store.create("tasks", task)
        store.create(
            "activity_events",
            ActivityEvent(project_id=project.id, task_id=task.id, event_type=ActivityEventType.TASK_CREATED, message=f"Created {task.desk.value} desk task."),
        )
    return project


@router.get("", response_model=list[ResearchProject])
def list_projects(store: StoreDep) -> list[ResearchProject]:
    return store.list("projects")


@router.get("/{project_id}", response_model=ResearchProject)
def get_project(project_id: str, store: StoreDep) -> ResearchProject:
    return _get_project_or_404(store, project_id)


@router.get("/{project_id}/tasks", response_model=list[ResearchTask])
def list_project_tasks(project_id: str, store: StoreDep) -> list[ResearchTask]:
    _get_project_or_404(store, project_id)
    return [task for task in store.list("tasks") if task.project_id == project_id]


@router.get("/{project_id}/activity-events", response_model=list[ActivityEvent])
def list_project_activity_events(project_id: str, store: StoreDep) -> list[ActivityEvent]:
    _get_project_or_404(store, project_id)
    return [event for event in store.list("activity_events") if event.project_id == project_id]


@router.get("/{project_id}/artifacts", response_model=list[ResearchArtifact])
def list_project_artifacts(project_id: str, store: StoreDep) -> list[ResearchArtifact]:
    _get_project_or_404(store, project_id)
    return [artifact for artifact in store.list("artifacts") if artifact.project_id == project_id]


@router.get("/{project_id}/decision-proposals", response_model=list[DecisionProposal])
def list_project_decision_proposals(project_id: str, store: StoreDep) -> list[DecisionProposal]:
    _get_project_or_404(store, project_id)
    return [proposal for proposal in store.list("proposals") if proposal.project_id == project_id]


@router.get("/{project_id}/investment-decisions", response_model=list[InvestmentDecision])
def list_project_investment_decisions(project_id: str, store: StoreDep) -> list[InvestmentDecision]:
    _get_project_or_404(store, project_id)
    return [decision for decision in store.list("decisions") if decision.project_id == project_id]


@router.get("/{project_id}/thesis", response_model=Thesis)
def get_project_thesis(project_id: str, store: StoreDep) -> Thesis:
    _get_project_or_404(store, project_id)
    theses = [thesis for thesis in store.list("theses") if thesis.project_id == project_id]
    if not theses:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thesis not found.")
    return sorted(theses, key=lambda thesis: thesis.version)[-1]


@router.get("/{project_id}/evidence", response_model=list[Evidence])
def list_project_evidence(project_id: str, store: StoreDep) -> list[Evidence]:
    _get_project_or_404(store, project_id)
    return [item for item in store.list("evidence") if item.project_id == project_id]


@router.get("/{project_id}/citations", response_model=list[EvidenceCitation])
def list_project_citations(project_id: str, store: StoreDep) -> list[EvidenceCitation]:
    _get_project_or_404(store, project_id)
    evidence_ids = {item.id for item in store.list("evidence") if item.project_id == project_id}
    return [citation for citation in store.list("citations") if citation.evidence_id in evidence_ids]


@router.post("/{project_id}/run-demo-workflow", response_model=DemoWorkflowResponse)
def run_project_demo_workflow(project_id: str, store: StoreDep) -> DemoWorkflowResponse:
    try:
        result = run_demo_workflow(store, project_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.") from exc
    except WorkflowError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return DemoWorkflowResponse(
        project=result.project,
        tasks=result.tasks,
        evidence=result.evidence,
        citations=result.citations,
        artifacts=result.artifacts,
        thesis=result.thesis,
        activity_events=result.activity_events,
    )


def _get_project_or_404(store: JsonStore, project_id: str) -> ResearchProject:
    project = store.get("projects", project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return project
