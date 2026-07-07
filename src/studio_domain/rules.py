from collections.abc import Iterable

from studio_schemas import EvidenceCitation, ProposalStatus


def missing_citation_ids(citation_ids: Iterable[str], citations: Iterable[EvidenceCitation]) -> set[str]:
    known_ids = {citation.id for citation in citations}
    return set(citation_ids) - known_ids


def ensure_citations_resolve(citation_ids: Iterable[str], citations: Iterable[EvidenceCitation]) -> None:
    missing = missing_citation_ids(citation_ids, citations)
    if missing:
        formatted = ", ".join(sorted(missing))
        raise ValueError(f"missing citations: {formatted}")


def ensure_pending_proposal(status: ProposalStatus) -> None:
    if status == ProposalStatus.PENDING_REVIEW:
        return
    raise ValueError("proposal is already decided")
