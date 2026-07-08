from dataclasses import dataclass
from typing import Any, Protocol

from studio_domain import ensure_project_citations_resolve
from studio_schemas import (
    ActivityEvent,
    ActivityEventType,
    Desk,
    Evidence,
    EvidenceCitation,
    ProjectStatus,
    ResearchArtifact,
    ResearchProject,
    ResearchTask,
    TaskStatus,
    Thesis,
    utc_now,
)
from studio_workflows.artifacts import generate_artifact, synthesize_thesis
from studio_workflows.fixtures import load_smr_evidence_bundle
from studio_workflows.planner import plan_tasks


class WorkflowError(RuntimeError):
    pass


class WorkflowStore(Protocol):
    def create(self, table: str, record: Any) -> Any: ...

    def get(self, table: str, record_id: str) -> Any | None: ...

    def list(self, table: str) -> list[Any]: ...

    def update(self, table: str, record_id: str, changes: dict) -> Any: ...


@dataclass(frozen=True)
class DemoWorkflowResult:
    project: ResearchProject
    tasks: list[ResearchTask]
    evidence: list[Evidence]
    citations: list[EvidenceCitation]
    artifacts: list[ResearchArtifact]
    thesis: Thesis
    activity_events: list[ActivityEvent]


def run_demo_workflow(store: WorkflowStore, project_id: str) -> DemoWorkflowResult:
    project = store.get("projects", project_id)
    if project is None:
        raise KeyError(f"project not found: {project_id}")

    project = store.update("projects", project.id, {"status": ProjectStatus.RUNNING, "updated_at": utc_now()})
    _create_event(store, project.id, None, ActivityEventType.WORKFLOW_STARTED, "Started deterministic SMR workflow.")

    tasks = _ensure_tasks(store, project)
    evidence, citations = _ensure_evidence_bundle(store, project)
    artifacts: list[ResearchArtifact] = []

    for task in tasks:
        task = store.update("tasks", task.id, {"status": TaskStatus.IN_PROGRESS, "updated_at": utc_now()})
        _create_event(store, project.id, task.id, ActivityEventType.TASK_STARTED, f"Started {task.desk.value} desk task.")

        desk_evidence = [item for item in evidence if item.metadata.get("desk") == task.desk.value]
        if not desk_evidence:
            store.update("tasks", task.id, {"status": TaskStatus.FAILED, "updated_at": utc_now()})
            store.update("projects", project.id, {"status": ProjectStatus.FAILED, "updated_at": utc_now()})
            _create_event(store, project.id, task.id, ActivityEventType.TASK_FAILED, f"No evidence fixture found for {task.desk.value} desk.")
            raise WorkflowError(f"missing evidence for {task.desk.value} desk")

        artifact = generate_artifact(task, desk_evidence, citations)
        _ensure_project_citations(store, project.id, artifact.citation_ids)
        artifact = _create_if_missing(store, "artifacts", artifact)
        _ensure_project_citations(store, project.id, artifact.citation_ids)
        artifacts.append(artifact)
        _create_event(store, project.id, task.id, ActivityEventType.ARTIFACT_CREATED, f"Created artifact for {task.desk.value} desk.")
        store.update("tasks", task.id, {"status": TaskStatus.COMPLETED, "updated_at": utc_now()})
        _create_event(store, project.id, task.id, ActivityEventType.TASK_COMPLETED, f"Completed {task.desk.value} desk task.")

    thesis = synthesize_thesis(project, artifacts, citations)
    _ensure_project_citations(store, project.id, thesis.citation_ids)
    _ensure_project_citations(store, project.id, thesis.candidate_asset.citation_ids)
    thesis = _create_if_missing(store, "theses", thesis)
    _ensure_project_citations(store, project.id, thesis.citation_ids)
    _ensure_project_citations(store, project.id, thesis.candidate_asset.citation_ids)
    _create_event(store, project.id, None, ActivityEventType.THESIS_CREATED, "Created version 1 thesis.")
    project = store.update("projects", project.id, {"status": ProjectStatus.COMPLETED, "updated_at": utc_now()})

    return DemoWorkflowResult(
        project=project,
        tasks=_project_tasks(store, project.id),
        evidence=_project_evidence(store, project.id),
        citations=_project_citations(store, project.id),
        artifacts=_project_artifacts(store, project.id),
        thesis=thesis,
        activity_events=_project_events(store, project.id),
    )


def _ensure_tasks(store: WorkflowStore, project: ResearchProject) -> list[ResearchTask]:
    existing = _project_tasks(store, project.id)
    if existing:
        return existing

    tasks = []
    for task in plan_tasks(project):
        tasks.append(_create_if_missing(store, "tasks", task))
        _create_event(store, project.id, task.id, ActivityEventType.TASK_CREATED, f"Created {task.desk.value} desk task.")
    return tasks


def _ensure_evidence_bundle(store: WorkflowStore, project: ResearchProject) -> tuple[list[Evidence], list[EvidenceCitation]]:
    existing_evidence = _project_evidence(store, project.id)
    existing_citations = _project_citations(store, project.id)
    existing_citations_by_evidence_id = _citations_by_evidence_id(existing_citations)
    bundle = load_smr_evidence_bundle(project)
    fixture_by_desk = {item.metadata.get("desk"): item for item in bundle.evidence}
    effective_evidence: list[Evidence] = []
    fixture_desks: list[str] = []

    for desk in Desk:
        user_evidence = [
            item
            for item in existing_evidence
            if item.metadata.get("origin") == "user" and item.metadata.get("desk") == desk.value and existing_citations_by_evidence_id.get(item.id)
        ]
        if user_evidence:
            effective_evidence.extend(user_evidence)
            continue

        fixture = fixture_by_desk.get(desk.value)
        if fixture is None:
            continue
        effective_evidence.append(_create_if_missing(store, "evidence", fixture))
        for citation in bundle.citations:
            if citation.evidence_id == fixture.id:
                _create_if_missing(store, "citations", citation)
        fixture_desks.append(desk.value)

    if fixture_desks:
        formatted = ", ".join(fixture_desks)
        _create_event(store, project.id, None, ActivityEventType.EVIDENCE_ATTACHED, f"Attached curated SMR evidence fixtures for {formatted} desks.")

    effective_evidence_ids = {item.id for item in effective_evidence}
    citations = [citation for citation in _project_citations(store, project.id) if citation.evidence_id in effective_evidence_ids]
    ensure_project_citations_resolve(project.id, [citation.id for citation in citations], _project_evidence(store, project.id), store.list("citations"))
    return effective_evidence, citations


def _create_if_missing(store: WorkflowStore, table: str, record):
    existing = store.get(table, record.id)
    if existing is not None:
        return existing
    return store.create(table, record)


def _create_event(store: WorkflowStore, project_id: str, task_id: str | None, event_type: ActivityEventType, message: str) -> ActivityEvent:
    return store.create(
        "activity_events",
        ActivityEvent(project_id=project_id, task_id=task_id, event_type=event_type, message=message),
    )


def _project_tasks(store: WorkflowStore, project_id: str) -> list[ResearchTask]:
    return [task for task in store.list("tasks") if task.project_id == project_id]


def _project_evidence(store: WorkflowStore, project_id: str) -> list[Evidence]:
    return [item for item in store.list("evidence") if item.project_id == project_id]


def _project_citations(store: WorkflowStore, project_id: str) -> list[EvidenceCitation]:
    evidence_ids = {item.id for item in _project_evidence(store, project_id)}
    return [citation for citation in store.list("citations") if citation.evidence_id in evidence_ids]


def _citations_by_evidence_id(citations: list[EvidenceCitation]) -> dict[str, list[EvidenceCitation]]:
    citations_by_evidence_id: dict[str, list[EvidenceCitation]] = {}
    for citation in citations:
        citations_by_evidence_id.setdefault(citation.evidence_id, []).append(citation)
    return citations_by_evidence_id


def _ensure_project_citations(store: WorkflowStore, project_id: str, citation_ids: list[str]) -> None:
    ensure_project_citations_resolve(project_id, citation_ids, _project_evidence(store, project_id), store.list("citations"))


def _project_artifacts(store: WorkflowStore, project_id: str) -> list[ResearchArtifact]:
    return [artifact for artifact in store.list("artifacts") if artifact.project_id == project_id]


def _project_events(store: WorkflowStore, project_id: str) -> list[ActivityEvent]:
    return [event for event in store.list("activity_events") if event.project_id == project_id]
