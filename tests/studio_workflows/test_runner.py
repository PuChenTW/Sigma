from pathlib import Path

import pytest

from studio_api.storage import JsonStore
from studio_schemas import Desk, Evidence, EvidenceCitation, EvidenceSourceType, ProjectStatus, ResearchArtifact, ResearchProject, TaskStatus
from studio_workflows import WorkflowError, plan_tasks, run_research_workflow


def test_research_workflow_creates_evidence_artifacts_and_thesis(tmp_path: Path) -> None:
    store = JsonStore(tmp_path / "studio.json")
    project = store.create("projects", ResearchProject(id="project_smr", title="SMR", topic="Small modular reactors", objective="Assess SMR exposure"))
    for task in plan_tasks(project):
        store.create("tasks", task)

    result = run_research_workflow(store, project.id)

    assert result.project.status == ProjectStatus.COMPLETED
    assert len(result.tasks) == 3
    assert {task.status for task in result.tasks} == {TaskStatus.COMPLETED}
    assert len(result.evidence) == 3
    assert len(result.citations) == 6
    assert len(result.artifacts) == 3
    assert all(artifact.citation_ids for artifact in result.artifacts)
    assert result.thesis.project_id == project.id
    assert set(result.thesis.artifact_ids) == {artifact.id for artifact in result.artifacts}
    assert set(result.thesis.citation_ids) == {citation_id for artifact in result.artifacts for citation_id in artifact.citation_ids}
    assert result.thesis.candidate_asset.symbol == "OKLO"
    assert result.activity_events
    assert {item.source_type for item in result.evidence} == {EvidenceSourceType.FIXTURE}


def test_research_workflow_can_rerun_without_duplicate_core_outputs(tmp_path: Path) -> None:
    store = JsonStore(tmp_path / "studio.json")
    project = store.create("projects", ResearchProject(id="project_smr", title="SMR", topic="Small modular reactors", objective="Assess SMR exposure"))
    for task in plan_tasks(project):
        store.create("tasks", task)

    run_research_workflow(store, project.id)
    run_research_workflow(store, project.id)

    assert len(store.list("evidence")) == 3
    assert len(store.list("citations")) == 6
    assert len(store.list("artifacts")) == 3
    assert len(store.list("theses")) == 1


def test_research_workflow_prefers_user_evidence_and_fills_missing_desks_with_fixtures(tmp_path: Path) -> None:
    store = JsonStore(tmp_path / "studio.json")
    project = store.create("projects", ResearchProject(id="project_smr", title="SMR", topic="Small modular reactors", objective="Assess SMR exposure"))
    for task in plan_tasks(project):
        store.create("tasks", task)
    industry_citation = _create_user_evidence(store, project, Desk.INDUSTRY, "Customer demand note")

    result = run_research_workflow(store, project.id)

    evidence_by_id = {item.id: item for item in result.evidence}
    artifact_by_desk = {task.desk: artifact for task in result.tasks for artifact in result.artifacts if artifact.task_id == task.id}
    assert len(result.evidence) == 3
    assert artifact_by_desk[Desk.INDUSTRY].citation_ids == [industry_citation.id]
    assert all(evidence_by_id[citation.evidence_id].metadata.get("origin") == "user" for citation in result.citations if citation.id in artifact_by_desk[Desk.INDUSTRY].citation_ids)
    assert {item.metadata.get("desk") for item in result.evidence if item.source_type == EvidenceSourceType.FIXTURE} == {Desk.MACRO_POLICY.value, Desk.FUNDAMENTAL.value}
    assert not any(item.title == "SMR demo evidence: industry demand" for item in result.evidence)


def test_research_workflow_uses_only_user_evidence_when_all_desks_are_covered(tmp_path: Path) -> None:
    store = JsonStore(tmp_path / "studio.json")
    project = store.create("projects", ResearchProject(id="project_smr", title="SMR", topic="Small modular reactors", objective="Assess SMR exposure"))
    for task in plan_tasks(project):
        store.create("tasks", task)
    user_citations = {_create_user_evidence(store, project, desk, f"{desk.value} note").id for desk in Desk}

    result = run_research_workflow(store, project.id)

    artifact_citation_ids = {citation_id for artifact in result.artifacts for citation_id in artifact.citation_ids}
    assert len(result.evidence) == 3
    assert len(result.citations) == 3
    assert {item.metadata.get("origin") for item in result.evidence} == {"user"}
    assert {item.source_type for item in result.evidence} == {EvidenceSourceType.NOTE}
    assert artifact_citation_ids == user_citations


def test_research_workflow_marks_failure_when_task_has_no_fixture_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    store = JsonStore(tmp_path / "studio.json")
    project = store.create("projects", ResearchProject(id="project_smr", title="SMR", topic="Small modular reactors", objective="Assess SMR exposure"))
    for task in plan_tasks(project):
        store.create("tasks", task)

    from studio_workflows import runner

    original_loader = runner.load_smr_evidence_bundle

    def load_without_fundamental(project: ResearchProject):
        bundle = original_loader(project)
        bundle.evidence.pop()
        return bundle

    monkeypatch.setattr(runner, "load_smr_evidence_bundle", load_without_fundamental)

    with pytest.raises(WorkflowError, match="missing evidence"):
        run_research_workflow(store, project.id)

    failed_tasks = [task for task in store.list("tasks") if task.status == TaskStatus.FAILED]
    assert store.get("projects", project.id).status == ProjectStatus.FAILED
    assert len(failed_tasks) == 1


def test_research_workflow_rejects_existing_artifact_with_missing_citation_id(tmp_path: Path) -> None:
    store = JsonStore(tmp_path / "studio.json")
    project = store.create("projects", ResearchProject(id="project_smr", title="SMR", topic="Small modular reactors", objective="Assess SMR exposure"))
    tasks = [store.create("tasks", task) for task in plan_tasks(project)]
    industry_task = next(task for task in tasks if task.desk == Desk.INDUSTRY)
    store.create(
        "artifacts",
        ResearchArtifact(
            id=f"artifact_{industry_task.id}",
            project_id=project.id,
            task_id=industry_task.id,
            title="Broken artifact",
            summary="Summary",
            findings=["Finding"],
            citation_ids=["citation_missing"],
        ),
    )

    with pytest.raises(ValueError, match="citation_missing"):
        run_research_workflow(store, project.id)


def test_research_workflow_rejects_existing_artifact_with_foreign_citation_id(tmp_path: Path) -> None:
    store = JsonStore(tmp_path / "studio.json")
    project = store.create("projects", ResearchProject(id="project_smr", title="SMR", topic="Small modular reactors", objective="Assess SMR exposure"))
    other_project = store.create("projects", ResearchProject(id="project_other", title="Other", topic="Other topic", objective="Other objective"))
    tasks = [store.create("tasks", task) for task in plan_tasks(project)]
    industry_task = next(task for task in tasks if task.desk == Desk.INDUSTRY)
    foreign_citation = _create_user_evidence(store, other_project, Desk.INDUSTRY, "Foreign note")
    store.create(
        "artifacts",
        ResearchArtifact(
            id=f"artifact_{industry_task.id}",
            project_id=project.id,
            task_id=industry_task.id,
            title="Foreign artifact",
            summary="Summary",
            findings=["Finding"],
            citation_ids=[foreign_citation.id],
        ),
    )

    with pytest.raises(ValueError, match=foreign_citation.id):
        run_research_workflow(store, project.id)


def _create_user_evidence(store: JsonStore, project: ResearchProject, desk: Desk, title: str) -> EvidenceCitation:
    evidence = store.create(
        "evidence",
        Evidence(
            id=f"evidence_{project.id}_{desk.value}_user",
            project_id=project.id,
            source_type=EvidenceSourceType.NOTE,
            title=title,
            summary=f"User summary for {desk.value}.",
            metadata={"desk": desk.value, "origin": "user"},
        ),
    )
    return store.create(
        "citations",
        EvidenceCitation(
            id=f"citation_{project.id}_{desk.value}_user",
            evidence_id=evidence.id,
            label=f"USER-{desk.value}",
            excerpt=f"User excerpt for {desk.value}.",
            location="manual note",
        ),
    )
