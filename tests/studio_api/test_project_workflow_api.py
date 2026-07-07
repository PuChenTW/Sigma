from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from studio_api import create_app
from studio_api.dependencies import get_store
from studio_api.storage import JsonStore


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    app = create_app()
    store = JsonStore(tmp_path / "studio.json")
    app.dependency_overrides[get_store] = lambda: store
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides = {}


def test_create_project_creates_fixed_tasks(client: TestClient) -> None:
    response = client.post("/research-projects", json={"topic": "Small modular reactors", "priority": "normal"})

    assert response.status_code == 201
    project = response.json()
    assert project["id"]
    assert project["topic"] == "Small modular reactors"

    tasks_response = client.get(f"/research-projects/{project['id']}/tasks")
    assert tasks_response.status_code == 200
    tasks = tasks_response.json()
    assert len(tasks) == 3
    assert {task["desk"] for task in tasks} == {"industry", "macro_policy", "fundamental"}
    assert {task["project_id"] for task in tasks} == {project["id"]}

    listed_projects = client.get("/research-projects").json()
    retrieved_project = client.get(f"/research-projects/{project['id']}").json()
    activity_events = client.get(f"/research-projects/{project['id']}/activity-events").json()

    assert [item["id"] for item in listed_projects] == [project["id"]]
    assert retrieved_project["id"] == project["id"]
    assert len(activity_events) == 4


def test_create_project_rejects_empty_topic(client: TestClient) -> None:
    response = client.post("/research-projects", json={"topic": ""})

    assert response.status_code == 422


def test_run_demo_workflow_exposes_artifacts_and_thesis(client: TestClient) -> None:
    project = client.post("/research-projects", json={"topic": "SMR investment opportunity"}).json()

    workflow_response = client.post(f"/research-projects/{project['id']}/run-demo-workflow")

    assert workflow_response.status_code == 200
    result = workflow_response.json()
    assert result["project"]["status"] == "completed"
    assert len(result["tasks"]) == 3
    assert len(result["evidence"]) == 3
    assert len(result["citations"]) == 6
    assert len(result["artifacts"]) == 3
    assert result["thesis"]["candidate_asset"]["symbol"] == "OKLO"

    artifacts_response = client.get(f"/research-projects/{project['id']}/artifacts")
    thesis_response = client.get(f"/research-projects/{project['id']}/thesis")

    assert artifacts_response.status_code == 200
    assert len(artifacts_response.json()) == 3
    assert thesis_response.status_code == 200
    assert thesis_response.json()["project_id"] == project["id"]
