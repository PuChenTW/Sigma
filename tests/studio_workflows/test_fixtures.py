from studio_domain import ensure_citations_resolve
from studio_schemas import Desk, ResearchProject
from studio_workflows import load_smr_evidence_bundle


def test_smr_fixture_citations_resolve_and_cover_desks() -> None:
    project = ResearchProject(id="project_smr", title="SMR", topic="Small modular reactors", objective="Assess SMR exposure")

    bundle = load_smr_evidence_bundle(project)

    evidence_ids = {item.id for item in bundle.evidence}
    assert {item.metadata["desk"] for item in bundle.evidence} == {Desk.INDUSTRY.value, Desk.MACRO_POLICY.value, Desk.FUNDAMENTAL.value}
    assert all(citation.evidence_id in evidence_ids for citation in bundle.citations)
    ensure_citations_resolve([citation.id for citation in bundle.citations], bundle.citations)
