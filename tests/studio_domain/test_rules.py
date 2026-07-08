import pytest

from studio_domain import ensure_citations_resolve, ensure_pending_proposal, ensure_project_citations_resolve, missing_citation_ids
from studio_schemas import Evidence, EvidenceCitation, EvidenceSourceType, ProposalStatus


def test_citation_resolution_reports_missing_ids() -> None:
    citations = [EvidenceCitation(id="citation_1", evidence_id="evidence_1", label="C1", excerpt="Excerpt", location="p.1")]

    assert missing_citation_ids(["citation_1", "citation_2"], citations) == {"citation_2"}

    with pytest.raises(ValueError, match="citation_2"):
        ensure_citations_resolve(["citation_2"], citations)


def test_pending_proposal_rule() -> None:
    ensure_pending_proposal(ProposalStatus.PENDING_REVIEW)

    with pytest.raises(ValueError, match="already decided"):
        ensure_pending_proposal(ProposalStatus.APPROVED)


def test_project_citation_resolution_rejects_missing_and_foreign_ids() -> None:
    project_evidence = [Evidence(id="evidence_1", project_id="project_1", source_type=EvidenceSourceType.NOTE, title="Note", summary="Summary")]
    citations = [
        EvidenceCitation(id="citation_1", evidence_id="evidence_1", label="C1", excerpt="Excerpt", location="p.1"),
        EvidenceCitation(id="citation_foreign", evidence_id="evidence_2", label="C2", excerpt="Excerpt", location="p.2"),
    ]

    ensure_project_citations_resolve("project_1", ["citation_1"], project_evidence, citations)

    with pytest.raises(ValueError, match="citation_missing"):
        ensure_project_citations_resolve("project_1", ["citation_missing"], project_evidence, citations)

    with pytest.raises(ValueError, match="citation_foreign"):
        ensure_project_citations_resolve("project_1", ["citation_foreign"], project_evidence, citations)
