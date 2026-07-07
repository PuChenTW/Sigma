from dataclasses import dataclass
from datetime import UTC, datetime

from studio_schemas import Desk, Evidence, EvidenceCitation, EvidenceSourceType, ResearchProject


@dataclass(frozen=True)
class EvidenceBundle:
    evidence: list[Evidence]
    citations: list[EvidenceCitation]


def load_smr_evidence_bundle(project: ResearchProject) -> EvidenceBundle:
    published_at = datetime(2026, 1, 15, tzinfo=UTC)
    evidence = [
        Evidence(
            id=f"evidence_{project.id}_industry",
            project_id=project.id,
            source_type=EvidenceSourceType.FIXTURE,
            title="SMR demo evidence: industry demand",
            published_at=published_at,
            summary="Offline MVP fixture covering power demand, nuclear capacity interest, and the commercial uncertainty around first-of-a-kind SMR deployment.",
            metadata={"desk": Desk.INDUSTRY.value, "fixture": "smr_demo"},
        ),
        Evidence(
            id=f"evidence_{project.id}_macro_policy",
            project_id=project.id,
            source_type=EvidenceSourceType.FIXTURE,
            title="SMR demo evidence: policy and financing",
            published_at=published_at,
            summary="Offline MVP fixture covering policy support, licensing friction, and rate-sensitive financing risk for nuclear development.",
            metadata={"desk": Desk.MACRO_POLICY.value, "fixture": "smr_demo"},
        ),
        Evidence(
            id=f"evidence_{project.id}_fundamental",
            project_id=project.id,
            source_type=EvidenceSourceType.FIXTURE,
            title="SMR demo evidence: candidate assets",
            published_at=published_at,
            summary="Offline MVP fixture comparing pure-play developer exposure with fuel-cycle and diversified nuclear supply-chain exposure.",
            metadata={"desk": Desk.FUNDAMENTAL.value, "fixture": "smr_demo"},
        ),
    ]
    citations = [
        EvidenceCitation(
            id=f"citation_{project.id}_industry_demand",
            evidence_id=evidence[0].id,
            label="IND-1",
            excerpt="Power demand growth and reliability needs create renewed interest in nuclear capacity, including modular reactor designs.",
            location="smr_demo:industry:1",
        ),
        EvidenceCitation(
            id=f"citation_{project.id}_industry_execution",
            evidence_id=evidence[0].id,
            label="IND-2",
            excerpt="Commercial SMR deployment remains exposed to first-of-a-kind construction, supplier qualification, and customer adoption risk.",
            location="smr_demo:industry:2",
        ),
        EvidenceCitation(
            id=f"citation_{project.id}_policy_support",
            evidence_id=evidence[1].id,
            label="POL-1",
            excerpt="Policy support improves the category setup, but licensing timelines and project finance still control the pace of deployment.",
            location="smr_demo:policy:1",
        ),
        EvidenceCitation(
            id=f"citation_{project.id}_financing_risk",
            evidence_id=evidence[1].id,
            label="POL-2",
            excerpt="Higher capital costs can delay nuclear project commitments even when long-term power demand remains attractive.",
            location="smr_demo:policy:2",
        ),
        EvidenceCitation(
            id=f"citation_{project.id}_candidate_oklo",
            evidence_id=evidence[2].id,
            label="FND-1",
            excerpt="OKLO offers direct advanced nuclear developer exposure, making it useful for committee review despite elevated execution risk.",
            location="smr_demo:fundamental:1",
        ),
        EvidenceCitation(
            id=f"citation_{project.id}_candidate_compare",
            evidence_id=evidence[2].id,
            label="FND-2",
            excerpt="Fuel-cycle and diversified nuclear names may offer lower binary risk, but they dilute direct SMR thesis exposure.",
            location="smr_demo:fundamental:2",
        ),
    ]
    return EvidenceBundle(evidence=evidence, citations=citations)
