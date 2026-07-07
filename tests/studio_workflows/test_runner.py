from pathlib import Path

import pytest

from studio_api.storage import JsonStore
from studio_schemas import ProjectStatus, ResearchProject, TaskStatus
from studio_workflows import WorkflowError, plan_tasks, run_demo_workflow


def test_demo_workflow_creates_evidence_artifacts_and_thesis(tmp_path: Path) -> None:
    store = JsonStore(tmp_path / "studio.json")
    project = store.create("projects", ResearchProject(id="project_smr", title="SMR", topic="Small modular reactors", objective="Assess SMR exposure"))
    for task in plan_tasks(project):
        store.create("tasks", task)

    result = run_demo_workflow(store, project.id)

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


def test_demo_workflow_can_rerun_without_duplicate_core_outputs(tmp_path: Path) -> None:
    store = JsonStore(tmp_path / "studio.json")
    project = store.create("projects", ResearchProject(id="project_smr", title="SMR", topic="Small modular reactors", objective="Assess SMR exposure"))
    for task in plan_tasks(project):
        store.create("tasks", task)

    run_demo_workflow(store, project.id)
    run_demo_workflow(store, project.id)

    assert len(store.list("evidence")) == 3
    assert len(store.list("citations")) == 6
    assert len(store.list("artifacts")) == 3
    assert len(store.list("theses")) == 1


def test_demo_workflow_marks_failure_when_task_has_no_fixture_evidence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
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
        run_demo_workflow(store, project.id)

    failed_tasks = [task for task in store.list("tasks") if task.status == TaskStatus.FAILED]
    assert store.get("projects", project.id).status == ProjectStatus.FAILED
    assert len(failed_tasks) == 1
