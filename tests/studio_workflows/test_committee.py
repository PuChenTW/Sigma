import pytest

from studio_schemas import CandidateAsset, ProposalAction, ProposalConviction, ResearchProject, Thesis
from studio_workflows import evaluate_committee


def test_stub_committee_creates_cited_watchlist_proposal() -> None:
    project = ResearchProject(id="project_smr", title="SMR", topic="Small modular reactors", objective="Assess SMR")
    thesis = Thesis(
        id="thesis_project_smr_v1",
        project_id=project.id,
        claim="SMR deserves committee review",
        evidence_for=["Evidence supports review"],
        invalidation_conditions=["Licensing stalls"],
        horizon="12 months",
        confidence=ProposalConviction.MEDIUM,
        candidate_asset=CandidateAsset(symbol="OKLO", name="Oklo Inc.", rationale="Direct exposure", artifact_ids=["artifact_1"], citation_ids=["citation_1"]),
        citation_ids=["citation_1", "citation_2"],
        artifact_ids=["artifact_1"],
    )

    proposal = evaluate_committee(project, thesis)

    assert proposal.id == "proposal_thesis_project_smr_v1_oklo"
    assert proposal.project_id == project.id
    assert proposal.thesis_id == thesis.id
    assert proposal.asset == "OKLO"
    assert proposal.action == ProposalAction.WATCHLIST
    assert proposal.conviction == ProposalConviction.MEDIUM
    assert proposal.citation_ids == ["citation_1"]
    assert proposal.primary_risks
    assert proposal.entry_conditions


def test_stub_committee_rejects_citations_not_linked_to_thesis() -> None:
    project = ResearchProject(id="project_smr", title="SMR", topic="Small modular reactors", objective="Assess SMR")
    thesis = Thesis(
        id="thesis_project_smr_v1",
        project_id=project.id,
        claim="SMR deserves committee review",
        evidence_for=["Evidence supports review"],
        invalidation_conditions=["Licensing stalls"],
        horizon="12 months",
        confidence=ProposalConviction.MEDIUM,
        candidate_asset=CandidateAsset(symbol="OKLO", name="Oklo Inc.", rationale="Direct exposure", artifact_ids=["artifact_1"], citation_ids=["citation_missing"]),
        citation_ids=["citation_1"],
        artifact_ids=["artifact_1"],
    )

    with pytest.raises(ValueError, match="not linked to thesis"):
        evaluate_committee(project, thesis)
