from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator
from typing_extensions import Self

from studio_schemas.enums import (
    ActivityEventType,
    DecisionType,
    Desk,
    EvidenceSourceType,
    ProjectStatus,
    ProposalAction,
    ProposalConviction,
    ProposalStatus,
    TaskStatus,
    ThesisStatus,
)

RecordId = Annotated[str, Field(min_length=1)]
NonEmptyText = Annotated[str, Field(min_length=1)]
CitationIdList = Annotated[list[RecordId], Field(min_length=1)]


def utc_now() -> datetime:
    return datetime.now(UTC)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


class StudioModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, validate_assignment=True)


class ResearchProject(StudioModel):
    id: RecordId = Field(default_factory=lambda: new_id("project"))
    title: NonEmptyText
    topic: NonEmptyText
    objective: NonEmptyText
    status: ProjectStatus = ProjectStatus.CREATED
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ResearchTask(StudioModel):
    id: RecordId = Field(default_factory=lambda: new_id("task"))
    project_id: RecordId
    desk: Desk
    title: NonEmptyText
    description: NonEmptyText
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Evidence(StudioModel):
    id: RecordId = Field(default_factory=lambda: new_id("evidence"))
    project_id: RecordId
    source_type: EvidenceSourceType
    title: NonEmptyText
    url: HttpUrl | None = None
    published_at: datetime | None = None
    summary: NonEmptyText
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceCitation(StudioModel):
    id: RecordId = Field(default_factory=lambda: new_id("citation"))
    evidence_id: RecordId
    label: NonEmptyText
    excerpt: NonEmptyText
    location: NonEmptyText


class ResearchArtifact(StudioModel):
    id: RecordId = Field(default_factory=lambda: new_id("artifact"))
    project_id: RecordId
    task_id: RecordId
    title: NonEmptyText
    summary: NonEmptyText
    findings: list[NonEmptyText] = Field(min_length=1)
    risks: list[NonEmptyText] = Field(default_factory=list)
    citation_ids: CitationIdList
    created_at: datetime = Field(default_factory=utc_now)


class CandidateAsset(StudioModel):
    symbol: NonEmptyText
    name: NonEmptyText
    rationale: NonEmptyText
    artifact_ids: list[RecordId] = Field(default_factory=list)
    citation_ids: list[RecordId] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_rationale_support(self) -> Self:
        if self.artifact_ids or self.citation_ids:
            return self
        raise ValueError("candidate asset rationale must reference artifacts or citations")


class Thesis(StudioModel):
    id: RecordId = Field(default_factory=lambda: new_id("thesis"))
    project_id: RecordId
    version: int = Field(default=1, ge=1)
    status: ThesisStatus = ThesisStatus.DRAFT
    claim: NonEmptyText
    evidence_for: list[NonEmptyText] = Field(min_length=1)
    evidence_against: list[NonEmptyText] = Field(default_factory=list)
    assumptions: list[NonEmptyText] = Field(default_factory=list)
    catalysts: list[NonEmptyText] = Field(default_factory=list)
    invalidation_conditions: list[NonEmptyText] = Field(min_length=1)
    horizon: NonEmptyText
    confidence: ProposalConviction
    candidate_asset: CandidateAsset
    citation_ids: CitationIdList
    artifact_ids: list[RecordId] = Field(min_length=1)


class DecisionProposal(StudioModel):
    id: RecordId = Field(default_factory=lambda: new_id("proposal"))
    project_id: RecordId
    thesis_id: RecordId
    asset: NonEmptyText
    action: ProposalAction
    status: ProposalStatus = ProposalStatus.PENDING_REVIEW
    conviction: ProposalConviction
    suggested_position_size: NonEmptyText
    horizon: NonEmptyText
    entry_conditions: list[NonEmptyText] = Field(min_length=1)
    invalidation_conditions: list[NonEmptyText] = Field(min_length=1)
    primary_risks: list[NonEmptyText] = Field(min_length=1)
    rationale: NonEmptyText
    citation_ids: CitationIdList


class InvestmentDecision(StudioModel):
    id: RecordId = Field(default_factory=lambda: new_id("decision"))
    project_id: RecordId
    proposal_id: RecordId
    thesis_id: RecordId
    decision: DecisionType
    user_note: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class ActivityEvent(StudioModel):
    id: RecordId = Field(default_factory=lambda: new_id("event"))
    project_id: RecordId
    task_id: RecordId | None = None
    event_type: ActivityEventType
    message: NonEmptyText
    created_at: datetime = Field(default_factory=utc_now)
