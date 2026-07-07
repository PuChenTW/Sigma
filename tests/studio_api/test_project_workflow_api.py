from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from studio_api import create_app
from studio_api.dependencies import get_store
from studio_api.storage import JsonStore


@pytest.fixture
def store(tmp_path: Path) -> JsonStore:
    return JsonStore(tmp_path / "studio.json")


@pytest.fixture
def client(store: JsonStore) -> Iterator[TestClient]:
    app = create_app()
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


def test_committee_evaluation_creates_proposal(client: TestClient, store: JsonStore) -> None:
    project = client.post("/research-projects", json={"topic": "SMR investment opportunity"}).json()
    client.post(f"/research-projects/{project['id']}/run-demo-workflow")

    response = client.post(f"/research-projects/{project['id']}/committee/evaluate")

    assert response.status_code == 200
    proposal = response.json()
    assert proposal["project_id"] == project["id"]
    assert proposal["thesis_id"]
    assert proposal["asset"] == "OKLO"
    assert proposal["status"] == "pending_review"
    assert proposal["action"] == "watchlist"
    assert proposal["horizon"]
    assert proposal["suggested_position_size"]
    assert proposal["primary_risks"]
    assert proposal["rationale"]
    assert proposal["citation_ids"]

    detail_response = client.get(f"/decision-proposals/{proposal['id']}")
    project_proposals = client.get(f"/research-projects/{project['id']}/decision-proposals").json()
    activity_events = client.get(f"/research-projects/{project['id']}/activity-events").json()
    citation_ids = {citation.id for citation in store.list("citations")}

    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == proposal["id"]
    assert [item["id"] for item in project_proposals] == [proposal["id"]]
    assert set(proposal["citation_ids"]) <= citation_ids
    assert any(event["event_type"] == "proposal_created" for event in activity_events)


def test_committee_evaluation_rejects_broken_candidate_citations(client: TestClient, store: JsonStore) -> None:
    project = client.post("/research-projects", json={"topic": "SMR investment opportunity"}).json()
    client.post(f"/research-projects/{project['id']}/run-demo-workflow")
    thesis = store.list("theses")[0]
    broken_candidate = thesis.candidate_asset.model_copy(update={"citation_ids": ["citation_missing"]})
    store.update("theses", thesis.id, {"candidate_asset": broken_candidate.model_dump(mode="json")})

    response = client.post(f"/research-projects/{project['id']}/committee/evaluate")

    assert response.status_code == 409


def test_committee_evaluation_requires_thesis(client: TestClient) -> None:
    project = client.post("/research-projects", json={"topic": "SMR investment opportunity"}).json()

    response = client.post(f"/research-projects/{project['id']}/committee/evaluate")

    assert response.status_code == 409


def test_approve_proposal_records_decision_and_blocks_repeat(client: TestClient, store: JsonStore) -> None:
    project = client.post("/research-projects", json={"topic": "SMR investment opportunity"}).json()
    client.post(f"/research-projects/{project['id']}/run-demo-workflow")
    proposal = client.post(f"/research-projects/{project['id']}/committee/evaluate").json()

    response = client.post(f"/decision-proposals/{proposal['id']}/approve", json={"user_note": "Track as watchlist only."})

    assert response.status_code == 200
    decision = response.json()
    assert decision["proposal_id"] == proposal["id"]
    assert decision["thesis_id"] == proposal["thesis_id"]
    assert decision["decision"] == "approved"
    assert decision["user_note"] == "Track as watchlist only."
    decision_record = store.get("decisions", decision["id"])
    project_decisions = client.get(f"/research-projects/{project['id']}/investment-decisions").json()
    assert decision_record is not None
    assert decision_record.proposal_id == proposal["id"]
    assert [item["id"] for item in project_decisions] == [decision["id"]]

    decided_proposal = client.get(f"/decision-proposals/{proposal['id']}").json()
    activity_events = client.get(f"/research-projects/{project['id']}/activity-events").json()
    repeated = client.post(f"/decision-proposals/{proposal['id']}/reject", json={})

    assert decided_proposal["status"] == "approved"
    assert repeated.status_code == 409
    assert any(event["event_type"] == "decision_recorded" for event in activity_events)


def test_reject_proposal_records_decision(client: TestClient) -> None:
    project = client.post("/research-projects", json={"topic": "SMR investment opportunity"}).json()
    client.post(f"/research-projects/{project['id']}/run-demo-workflow")
    proposal = client.post(f"/research-projects/{project['id']}/committee/evaluate").json()

    response = client.post(f"/decision-proposals/{proposal['id']}/reject", json={"user_note": "Risk is too high."})

    assert response.status_code == 200
    assert response.json()["decision"] == "rejected"
    assert client.get(f"/decision-proposals/{proposal['id']}").json()["status"] == "rejected"
    assert client.post(f"/decision-proposals/{proposal['id']}/reject", json={}).status_code == 409
