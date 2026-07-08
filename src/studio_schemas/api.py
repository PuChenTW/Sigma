from typing import Literal

from pydantic import Field, HttpUrl

from studio_schemas.enums import DecisionType, Desk, EvidenceSourceType, Priority
from studio_schemas.models import ActivityEvent, Evidence, EvidenceCitation, NonEmptyText, RecordId, ResearchArtifact, ResearchProject, ResearchTask, StudioModel, Thesis


class CreateResearchProjectRequest(StudioModel):
    topic: NonEmptyText
    priority: Priority = Priority.NORMAL
    facets: list[str] = Field(default_factory=list)


class CreateCitationInput(StudioModel):
    label: NonEmptyText | None = None
    excerpt: NonEmptyText
    location: NonEmptyText


class CreateEvidenceRequest(StudioModel):
    source_type: Literal[EvidenceSourceType.NOTE, EvidenceSourceType.ARTICLE]
    desk: Desk
    title: NonEmptyText
    url: HttpUrl | None = None
    summary: NonEmptyText
    citations: list[CreateCitationInput] = Field(min_length=1)


class CreateEvidenceResponse(StudioModel):
    evidence: Evidence
    citations: list[EvidenceCitation]


class DecisionRequest(StudioModel):
    user_note: str | None = None


class HealthResponse(StudioModel):
    status: str = "ok"


class NotImplementedResponse(StudioModel):
    detail: str
    phase: str = "phase_2"


class InvestmentDecisionResponse(StudioModel):
    proposal_id: RecordId
    decision: DecisionType


class DemoWorkflowResponse(StudioModel):
    project: ResearchProject
    tasks: list[ResearchTask]
    evidence: list[Evidence]
    citations: list[EvidenceCitation]
    artifacts: list[ResearchArtifact]
    thesis: Thesis
    activity_events: list[ActivityEvent]
