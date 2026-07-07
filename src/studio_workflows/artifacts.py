from collections.abc import Sequence

from studio_domain import ensure_citations_resolve
from studio_schemas import (
    CandidateAsset,
    Desk,
    Evidence,
    EvidenceCitation,
    ProposalConviction,
    ResearchArtifact,
    ResearchProject,
    ResearchTask,
    Thesis,
    ThesisStatus,
)


def generate_artifact(task: ResearchTask, evidence: Sequence[Evidence], citations: Sequence[EvidenceCitation]) -> ResearchArtifact:
    evidence_ids = {item.id for item in evidence}
    citation_ids = [citation.id for citation in citations if citation.evidence_id in evidence_ids]
    ensure_citations_resolve(citation_ids, citations)
    if not citation_ids:
        raise ValueError(f"task {task.id} has no citations")

    summaries = {
        Desk.INDUSTRY: "SMR demand is improving, but investability depends on deployment credibility rather than category enthusiasm alone.",
        Desk.MACRO_POLICY: "Policy support is constructive, while financing cost and licensing duration remain the gating risks.",
        Desk.FUNDAMENTAL: "OKLO is the cleanest committee candidate for direct advanced nuclear exposure, with high execution risk.",
    }
    findings = {
        Desk.INDUSTRY: [
            "Reliable clean-power demand supports renewed nuclear interest.",
            "First-of-a-kind deployment risk keeps the industry thesis from being purely demand-driven.",
        ],
        Desk.MACRO_POLICY: [
            "Policy support improves the setup for nuclear development.",
            "Financing and licensing constraints can still delay commercial milestones.",
        ],
        Desk.FUNDAMENTAL: [
            "OKLO gives direct advanced nuclear developer exposure.",
            "Diversified alternatives reduce binary risk but weaken SMR-specific upside.",
        ],
    }
    risks = {
        Desk.INDUSTRY: ["Supplier qualification and customer adoption could take longer than expected."],
        Desk.MACRO_POLICY: ["Higher capital costs could defer nuclear project commitments."],
        Desk.FUNDAMENTAL: ["The candidate asset carries elevated execution and valuation risk."],
    }

    return ResearchArtifact(
        id=f"artifact_{task.id}",
        project_id=task.project_id,
        task_id=task.id,
        title=f"{task.title} artifact",
        summary=summaries[task.desk],
        findings=findings[task.desk],
        risks=risks[task.desk],
        citation_ids=citation_ids,
    )


def synthesize_thesis(project: ResearchProject, artifacts: Sequence[ResearchArtifact], citations: Sequence[EvidenceCitation]) -> Thesis:
    if not artifacts:
        raise ValueError("cannot synthesize thesis without artifacts")

    artifact_ids = [artifact.id for artifact in artifacts]
    citation_ids = sorted({citation_id for artifact in artifacts for citation_id in artifact.citation_ids})
    ensure_citations_resolve(citation_ids, citations)

    return Thesis(
        id=f"thesis_{project.id}_v1",
        project_id=project.id,
        version=1,
        status=ThesisStatus.ACTIVE,
        claim="SMR-linked equities deserve bounded committee review, but only as high-risk exposure tied to execution milestones.",
        evidence_for=[
            "Reliable clean-power demand and policy support create a constructive category backdrop.",
            "A direct developer candidate gives focused exposure if the committee accepts first-of-a-kind execution risk.",
        ],
        evidence_against=[
            "Commercial deployment, licensing, financing, and valuation risks remain material.",
            "More diversified nuclear exposures may be better risk-adjusted if direct SMR execution confidence is low.",
        ],
        assumptions=[
            "The user wants topic-driven research converted into one reviewable investment candidate.",
            "The MVP demo uses curated offline evidence rather than live market data.",
        ],
        catalysts=[
            "Customer announcements, licensing progress, project finance milestones, and supply-chain validation.",
        ],
        invalidation_conditions=[
            "Material licensing delay, failed customer conversion, financing deterioration, or evidence that diversified nuclear exposure dominates direct SMR exposure.",
        ],
        horizon="12-24 months",
        confidence=ProposalConviction.MEDIUM,
        candidate_asset=CandidateAsset(
            symbol="OKLO",
            name="Oklo Inc.",
            rationale="OKLO is the clearest deterministic candidate for direct advanced nuclear exposure in the SMR demo, while the artifact set preserves the execution risks.",
            artifact_ids=artifact_ids,
            citation_ids=citation_ids,
        ),
        citation_ids=citation_ids,
        artifact_ids=artifact_ids,
    )
