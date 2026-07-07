from dataclasses import dataclass
from typing import Protocol

from studio_schemas import DecisionProposal, ProposalAction, ResearchProject, Thesis


@dataclass(frozen=True)
class CommitteeInput:
    project: ResearchProject
    thesis: Thesis


class CommitteeEvaluator(Protocol):
    def evaluate(self, committee_input: CommitteeInput) -> DecisionProposal: ...


class StubCommitteeEvaluator:
    def evaluate(self, committee_input: CommitteeInput) -> DecisionProposal:
        project = committee_input.project
        thesis = committee_input.thesis
        asset = thesis.candidate_asset

        citation_ids = asset.citation_ids or thesis.citation_ids
        missing = set(citation_ids) - set(thesis.citation_ids)
        if missing:
            formatted = ", ".join(sorted(missing))
            raise ValueError(f"proposal citations are not linked to thesis: {formatted}")

        return DecisionProposal(
            id=f"proposal_{thesis.id}_{asset.symbol.lower()}",
            project_id=project.id,
            thesis_id=thesis.id,
            asset=asset.symbol,
            action=ProposalAction.WATCHLIST,
            conviction=thesis.confidence,
            suggested_position_size="0% until user approval; watchlist candidate only in MVP.",
            horizon=thesis.horizon,
            entry_conditions=[
                "Escalate only after the user accepts high execution risk and validates near-term milestones.",
                "Treat customer, licensing, and financing progress as required confirmation before sizing.",
            ],
            invalidation_conditions=thesis.invalidation_conditions,
            primary_risks=[
                "First-of-a-kind deployment risk can delay or invalidate the direct exposure thesis.",
                "Valuation can move faster than evidence quality in a narrow thematic trade.",
            ],
            rationale=(
                f"{asset.symbol} is the deterministic committee candidate because the thesis identifies it as the clearest direct "
                "advanced nuclear exposure while preserving the artifact-backed execution risks."
            ),
            citation_ids=citation_ids,
        )


def evaluate_committee(project: ResearchProject, thesis: Thesis, evaluator: CommitteeEvaluator | None = None) -> DecisionProposal:
    committee = evaluator or StubCommitteeEvaluator()
    return committee.evaluate(CommitteeInput(project=project, thesis=thesis))
