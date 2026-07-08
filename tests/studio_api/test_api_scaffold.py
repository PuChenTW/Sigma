from fastapi.testclient import TestClient

from studio_api import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_mvp_route_structure_is_registered() -> None:
    client = TestClient(create_app())

    paths = client.get("/openapi.json").json()["paths"]

    assert "/research-projects" in paths
    assert "/research-projects/{project_id}" in paths
    assert "/research-projects/{project_id}/tasks" in paths
    assert "/research-projects/{project_id}/activity-events" in paths
    assert "/research-projects/{project_id}/evidence" in paths
    assert "post" in paths["/research-projects/{project_id}/evidence"]
    assert "/research-projects/{project_id}/citations" in paths
    assert "/research-projects/{project_id}/artifacts" in paths
    assert "/research-projects/{project_id}/decision-proposals" in paths
    assert "/research-projects/{project_id}/investment-decisions" in paths
    assert "/research-projects/{project_id}/thesis" in paths
    assert "/research-projects/{project_id}/run-demo-workflow" in paths
    assert "/research-projects/{project_id}/committee/evaluate" in paths
    assert "/decision-proposals/{proposal_id}" in paths
    assert "/decision-proposals/{proposal_id}/approve" in paths
    assert "/decision-proposals/{proposal_id}/reject" in paths
