from pathlib import Path

import pytest

from studio_api.storage import TABLE_MODELS, JsonStore
from studio_schemas import (
    ActivityEvent,
    ActivityEventType,
    CandidateAsset,
    DecisionProposal,
    Desk,
    Evidence,
    EvidenceCitation,
    EvidenceSourceType,
    InvestmentDecision,
    ProjectStatus,
    ProposalAction,
    ProposalConviction,
    ResearchArtifact,
    ResearchProject,
    ResearchTask,
    Thesis,
)
from studio_schemas.enums import DecisionType


def sample_records() -> dict:
    project = ResearchProject(id="project_1", title="SMR research", topic="Small modular reactors", objective="Assess SMR exposure")
    task = ResearchTask(id="task_1", project_id=project.id, desk=Desk.INDUSTRY, title="Industry", description="Assess industry demand")
    evidence = Evidence(id="evidence_1", project_id=project.id, source_type=EvidenceSourceType.FIXTURE, title="Fixture", summary="Summary")
    citation = EvidenceCitation(id="citation_1", evidence_id=evidence.id, label="C1", excerpt="Excerpt", location="fixture:1")
    artifact = ResearchArtifact(
        id="artifact_1",
        project_id=project.id,
        task_id=task.id,
        title="Artifact",
        summary="Summary",
        findings=["Finding"],
        citation_ids=[citation.id],
    )
    thesis = Thesis(
        id="thesis_1",
        project_id=project.id,
        claim="Claim",
        evidence_for=["For"],
        invalidation_conditions=["Invalidation"],
        horizon="12 months",
        confidence=ProposalConviction.MEDIUM,
        candidate_asset=CandidateAsset(symbol="SMR", name="NuScale Power", rationale="Rationale", artifact_ids=[artifact.id]),
        citation_ids=[citation.id],
        artifact_ids=[artifact.id],
    )
    proposal = DecisionProposal(
        id="proposal_1",
        project_id=project.id,
        thesis_id=thesis.id,
        asset="SMR",
        action=ProposalAction.WATCHLIST,
        conviction=ProposalConviction.MEDIUM,
        suggested_position_size="0%",
        horizon="12 months",
        entry_conditions=["Review"],
        invalidation_conditions=["Break"],
        primary_risks=["Risk"],
        rationale="Rationale",
        citation_ids=[citation.id],
    )
    decision = InvestmentDecision(id="decision_1", project_id=project.id, proposal_id=proposal.id, thesis_id=thesis.id, decision=DecisionType.APPROVED)
    event = ActivityEvent(id="event_1", project_id=project.id, task_id=task.id, event_type=ActivityEventType.PROJECT_CREATED, message="Created")

    return {
        "activity_events": event,
        "artifacts": artifact,
        "citations": citation,
        "decisions": decision,
        "evidence": evidence,
        "projects": project,
        "proposals": proposal,
        "tasks": task,
        "theses": thesis,
    }


def test_store_creates_lists_gets_and_survives_reopen(tmp_path: Path) -> None:
    path = tmp_path / "studio.json"
    store = JsonStore(path)
    records = sample_records()

    for table, record in records.items():
        store.create(table, record)

    reopened = JsonStore(path)

    assert set(TABLE_MODELS) == set(records)
    for table, record in records.items():
        assert reopened.get(table, record.id).model_dump(mode="json") == record.model_dump(mode="json")
        assert [item.model_dump(mode="json") for item in reopened.list(table)] == [record.model_dump(mode="json")]


def test_store_updates_records(tmp_path: Path) -> None:
    store = JsonStore(tmp_path / "studio.json")
    project = store.create("projects", sample_records()["projects"])

    updated = store.update("projects", project.id, {"status": ProjectStatus.RUNNING})

    assert updated.status == ProjectStatus.RUNNING


def test_store_rejects_duplicate_ids(tmp_path: Path) -> None:
    store = JsonStore(tmp_path / "studio.json")
    project = sample_records()["projects"]
    store.create("projects", project)

    with pytest.raises(ValueError, match="already exists"):
        store.create("projects", project)


def test_store_validates_update_payload(tmp_path: Path) -> None:
    store = JsonStore(tmp_path / "studio.json")
    task = store.create("tasks", sample_records()["tasks"])

    with pytest.raises(ValueError):
        store.update("tasks", task.id, {"status": "not_a_status"})
