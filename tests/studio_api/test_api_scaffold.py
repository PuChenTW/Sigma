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


def test_openapi_documents_route_purpose_and_tags() -> None:
    client = TestClient(create_app())

    schema = client.get("/openapi.json").json()
    tag_descriptions = {tag["name"]: tag.get("description") for tag in schema["tags"]}

    assert tag_descriptions["health"]
    assert tag_descriptions["research-projects"]
    assert tag_descriptions["committee"]
    assert tag_descriptions["decision-proposals"]

    for path, methods in schema["paths"].items():
        for method, operation in methods.items():
            if method == "parameters":
                continue
            assert operation["tags"], f"{method.upper()} {path} is missing tags"
            assert operation["summary"], f"{method.upper()} {path} is missing summary"
            assert operation.get("description"), f"{method.upper()} {path} is missing description"
            success_responses = [response for status_code, response in operation["responses"].items() if status_code.startswith("2")]
            assert success_responses, f"{method.upper()} {path} is missing a 2xx response"
            assert all(response.get("description") != "Successful Response" for response in success_responses), f"{method.upper()} {path} has default response description"


def test_openapi_documents_state_transition_boundaries() -> None:
    client = TestClient(create_app())

    paths = client.get("/openapi.json").json()["paths"]

    approve_description = paths["/decision-proposals/{proposal_id}/approve"]["post"]["description"]
    evaluate_description = paths["/research-projects/{project_id}/committee/evaluate"]["post"]["description"]

    assert "does not execute a trade" in approve_description
    assert "does not own research projects" in evaluate_description
