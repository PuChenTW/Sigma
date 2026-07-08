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
    response = client.post("/research-projects", json={"topic": "Small modular reactors"})

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


@pytest.mark.parametrize("stale_field", ["priority", "facets"])
def test_create_project_rejects_removed_planning_fields(client: TestClient, stale_field: str) -> None:
    payload = {"topic": "Small modular reactors", stale_field: "normal" if stale_field == "priority" else ["industry"]}

    response = client.post("/research-projects", json=payload)

    assert response.status_code == 422


def test_create_project_evidence_supports_note_and_article(client: TestClient) -> None:
    project = client.post("/research-projects", json={"topic": "SMR evidence workbench"}).json()

    note_response = client.post(
        f"/research-projects/{project['id']}/evidence",
        json={
            "source_type": "note",
            "desk": "industry",
            "title": "Customer demand note",
            "summary": "A utility buyer needs reliable clean power capacity.",
            "citations": [{"excerpt": "We need firm clean power by 2030.", "location": "manual note"}],
        },
    )
    article_response = client.post(
        f"/research-projects/{project['id']}/evidence",
        json={
            "source_type": "article",
            "desk": "macro_policy",
            "title": "Policy update",
            "url": "https://example.com/policy-update",
            "summary": "A policy article explains support for advanced nuclear development.",
            "citations": [{"label": "POLICY-NOTE", "excerpt": "Policy support remains constructive.", "location": "paragraph 2"}],
        },
    )

    assert note_response.status_code == 201
    assert article_response.status_code == 201

    note = note_response.json()
    article = article_response.json()
    assert note["evidence"]["project_id"] == project["id"]
    assert note["evidence"]["source_type"] == "note"
    assert note["evidence"]["metadata"] == {"desk": "industry", "origin": "user"}
    assert note["citations"][0]["label"] == "USER-1"
    assert article["evidence"]["source_type"] == "article"
    assert article["evidence"]["url"] == "https://example.com/policy-update"
    assert article["citations"][0]["label"] == "POLICY-NOTE"

    evidence = client.get(f"/research-projects/{project['id']}/evidence").json()
    citations = client.get(f"/research-projects/{project['id']}/citations").json()
    activity_events = client.get(f"/research-projects/{project['id']}/activity-events").json()

    assert {item["id"] for item in evidence} == {note["evidence"]["id"], article["evidence"]["id"]}
    assert {citation["id"] for citation in citations} == {note["citations"][0]["id"], article["citations"][0]["id"]}
    assert any(event["message"] == "Added user evidence for industry desk." for event in activity_events)
    assert any(event["message"] == "Added user evidence for macro_policy desk." for event in activity_events)


def test_create_project_evidence_rejects_missing_project(client: TestClient) -> None:
    response = client.post(
        "/research-projects/project_missing/evidence",
        json={
            "source_type": "note",
            "desk": "industry",
            "title": "Customer demand note",
            "summary": "A utility buyer needs reliable clean power capacity.",
            "citations": [{"excerpt": "We need firm clean power by 2030.", "location": "manual note"}],
        },
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_type", "fixture"),
        ("desk", "quant"),
        ("summary", ""),
    ],
)
def test_create_project_evidence_rejects_invalid_evidence_fields(client: TestClient, field: str, value: str) -> None:
    project = client.post("/research-projects", json={"topic": "SMR evidence workbench"}).json()
    payload = {
        "source_type": "note",
        "desk": "industry",
        "title": "Customer demand note",
        "summary": "A utility buyer needs reliable clean power capacity.",
        "citations": [{"excerpt": "We need firm clean power by 2030.", "location": "manual note"}],
    }
    payload[field] = value

    response = client.post(f"/research-projects/{project['id']}/evidence", json=payload)

    assert response.status_code == 422


@pytest.mark.parametrize("citation", [{"excerpt": "", "location": "manual note"}, {"excerpt": "Quote", "location": ""}])
def test_create_project_evidence_rejects_invalid_citation_fields(client: TestClient, citation: dict[str, str]) -> None:
    project = client.post("/research-projects", json={"topic": "SMR evidence workbench"}).json()

    response = client.post(
        f"/research-projects/{project['id']}/evidence",
        json={
            "source_type": "note",
            "desk": "industry",
            "title": "Customer demand note",
            "summary": "A utility buyer needs reliable clean power capacity.",
            "citations": [citation],
        },
    )

    assert response.status_code == 422


def test_run_research_workflow_exposes_artifacts_and_thesis(client: TestClient) -> None:
    project = client.post("/research-projects", json={"topic": "SMR investment opportunity"}).json()

    workflow_response = client.post(f"/research-projects/{project['id']}/run-research")

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
    client.post(f"/research-projects/{project['id']}/run-research")

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
    client.post(f"/research-projects/{project['id']}/run-research")
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
    client.post(f"/research-projects/{project['id']}/run-research")
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
    client.post(f"/research-projects/{project['id']}/run-research")
    proposal = client.post(f"/research-projects/{project['id']}/committee/evaluate").json()

    response = client.post(f"/decision-proposals/{proposal['id']}/reject", json={"user_note": "Risk is too high."})

    assert response.status_code == 200
    assert response.json()["decision"] == "rejected"
    assert client.get(f"/decision-proposals/{proposal['id']}").json()["status"] == "rejected"
    assert client.post(f"/decision-proposals/{proposal['id']}/reject", json={}).status_code == 409
