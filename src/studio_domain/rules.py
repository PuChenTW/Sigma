from collections.abc import Iterable

from studio_schemas import Evidence, EvidenceCitation, ProposalStatus


def missing_citation_ids(citation_ids: Iterable[str], citations: Iterable[EvidenceCitation]) -> set[str]:
    known_ids = {citation.id for citation in citations}
    return set(citation_ids) - known_ids


def ensure_citations_resolve(citation_ids: Iterable[str], citations: Iterable[EvidenceCitation]) -> None:
    missing = missing_citation_ids(citation_ids, citations)
    if missing:
        formatted = ", ".join(sorted(missing))
        raise ValueError(f"missing citations: {formatted}")


def project_citation_issues(
    project_id: str,
    citation_ids: Iterable[str],
    project_evidence: Iterable[Evidence],
    citations: Iterable[EvidenceCitation],
) -> set[str]:
    project_evidence_ids = {item.id for item in project_evidence if item.project_id == project_id}
    citation_by_id = {citation.id: citation for citation in citations}

    bad_ids = set()
    for citation_id in citation_ids:
        citation = citation_by_id.get(citation_id)
        if citation is None or citation.evidence_id not in project_evidence_ids:
            bad_ids.add(citation_id)
    return bad_ids


def ensure_project_citations_resolve(
    project_id: str,
    citation_ids: Iterable[str],
    project_evidence: Iterable[Evidence],
    citations: Iterable[EvidenceCitation],
) -> None:
    bad_ids = project_citation_issues(project_id, citation_ids, project_evidence, citations)
    if bad_ids:
        formatted = ", ".join(sorted(bad_ids))
        raise ValueError(f"missing or foreign citations: {formatted}")


def ensure_pending_proposal(status: ProposalStatus) -> None:
    if status == ProposalStatus.PENDING_REVIEW:
        return
    raise ValueError("proposal is already decided")
