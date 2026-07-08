import pytest
from pydantic import ValidationError

from studio_schemas import (
    ActivityEvent,
    ActivityEventType,
    CandidateAsset,
    CreateEvidenceRequest,
    DecisionProposal,
    Desk,
    Evidence,
    EvidenceCitation,
    EvidenceSourceType,
    InvestmentDecision,
    ProposalAction,
    ProposalConviction,
    ResearchArtifact,
    ResearchProject,
    ResearchTask,
    Thesis,
)
from studio_schemas.enums import DecisionType


def test_artifact_rejects_missing_citations() -> None:
    with pytest.raises(ValidationError, match="citation_ids"):
        ResearchArtifact(
            project_id="project_1",
            task_id="task_1",
            title="Industry artifact",
            summary="Summary",
            findings=["Finding"],
            citation_ids=[],
        )


def test_create_evidence_request_accepts_note_source_type() -> None:
    request = CreateEvidenceRequest(
        source_type=EvidenceSourceType.NOTE,
        desk=Desk.INDUSTRY,
        title="Customer interview note",
        summary="A utility customer described rising interest in modular nuclear capacity.",
        citations=[{"excerpt": "We need firm clean power by 2030.", "location": "manual note"}],
    )

    assert request.source_type == EvidenceSourceType.NOTE
    assert request.citations[0].label is None


def test_create_evidence_request_accepts_article_source_type_and_optional_label() -> None:
    request = CreateEvidenceRequest(
        source_type="article",
        desk=Desk.MACRO_POLICY,
        title="Nuclear licensing update",
        url="https://example.com/nuclear-licensing",
        summary="The article summarizes licensing changes relevant to advanced nuclear projects.",
        citations=[{"label": "NRC-1", "excerpt": "Regulators proposed a staged licensing path.", "location": "paragraph 4"}],
    )

    assert request.source_type == EvidenceSourceType.ARTICLE
    assert str(request.url) == "https://example.com/nuclear-licensing"
    assert request.citations[0].label == "NRC-1"


def test_create_evidence_request_rejects_empty_summary() -> None:
    with pytest.raises(ValidationError, match="summary"):
        CreateEvidenceRequest(
            source_type=EvidenceSourceType.NOTE,
            desk=Desk.FUNDAMENTAL,
            title="Company note",
            summary=" ",
            citations=[{"excerpt": "Management expects first revenue after deployment.", "location": "manual note"}],
        )


def test_create_evidence_request_requires_citation_excerpt() -> None:
    with pytest.raises(ValidationError, match="excerpt"):
        CreateEvidenceRequest(
            source_type=EvidenceSourceType.NOTE,
            desk=Desk.INDUSTRY,
            title="Demand note",
            summary="Summary of source.",
            citations=[{"location": "manual note"}],
        )


def test_create_evidence_request_requires_citation_location() -> None:
    with pytest.raises(ValidationError, match="location"):
        CreateEvidenceRequest(
            source_type=EvidenceSourceType.ARTICLE,
            desk=Desk.MACRO_POLICY,
            title="Policy article",
            summary="Summary of source.",
            citations=[{"excerpt": "Policy support remains constructive."}],
        )


def test_schemas_cover_mvp_records() -> None:
    project = ResearchProject(title="SMR research", topic="Small modular reactors", objective="Assess investable SMR exposure")
    task = ResearchTask(project_id=project.id, desk=Desk.INDUSTRY, title="Industry", description="Assess industry demand")
    evidence = Evidence(project_id=project.id, source_type=EvidenceSourceType.FIXTURE, title="Fixture", summary="Source summary")
    citation = EvidenceCitation(evidence_id=evidence.id, label="C1", excerpt="Evidence excerpt", location="fixture:1")
    artifact = ResearchArtifact(
        project_id=project.id,
        task_id=task.id,
        title="Industry artifact",
        summary="Summary",
        findings=["Nuclear load growth supports the category"],
        citation_ids=[citation.id],
    )
    candidate = CandidateAsset(symbol="SMR", name="NuScale Power", rationale="Pure-play exposure", artifact_ids=[artifact.id])
    thesis = Thesis(
        project_id=project.id,
        claim="SMR exposure is worth committee review",
        evidence_for=["Policy and power-demand support"],
        invalidation_conditions=["Financing conditions deteriorate"],
        horizon="12 months",
        confidence=ProposalConviction.MEDIUM,
        candidate_asset=candidate,
        citation_ids=[citation.id],
        artifact_ids=[artifact.id],
    )
    proposal = DecisionProposal(
        project_id=project.id,
        thesis_id=thesis.id,
        asset="SMR",
        action=ProposalAction.WATCHLIST,
        conviction=ProposalConviction.MEDIUM,
        suggested_position_size="0%",
        horizon="12 months",
        entry_conditions=["Wait for committee approval"],
        invalidation_conditions=["Thesis breaks"],
        primary_risks=["Execution risk"],
        rationale="Needs bounded review",
        citation_ids=[citation.id],
    )
    decision = InvestmentDecision(project_id=project.id, proposal_id=proposal.id, thesis_id=thesis.id, decision=DecisionType.REJECTED)
    event = ActivityEvent(project_id=project.id, task_id=task.id, event_type=ActivityEventType.TASK_CREATED, message="Task created")

    assert project.status == "created"
    assert task.status == "pending"
    assert proposal.status == "pending_review"
    assert decision.decision == "rejected"
    assert event.event_type == "task_created"


def test_candidate_asset_requires_support_reference() -> None:
    with pytest.raises(ValidationError, match="rationale must reference"):
        CandidateAsset(symbol="SMR", name="NuScale Power", rationale="Pure-play exposure")
