import pytest

from studio_domain import ensure_citations_resolve, ensure_pending_proposal, missing_citation_ids
from studio_schemas import EvidenceCitation, ProposalStatus


def test_citation_resolution_reports_missing_ids() -> None:
    citations = [EvidenceCitation(id="citation_1", evidence_id="evidence_1", label="C1", excerpt="Excerpt", location="p.1")]

    assert missing_citation_ids(["citation_1", "citation_2"], citations) == {"citation_2"}

    with pytest.raises(ValueError, match="citation_2"):
        ensure_citations_resolve(["citation_2"], citations)


def test_pending_proposal_rule() -> None:
    ensure_pending_proposal(ProposalStatus.PENDING_REVIEW)

    with pytest.raises(ValueError, match="already decided"):
        ensure_pending_proposal(ProposalStatus.APPROVED)
