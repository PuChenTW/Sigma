from pydantic import Field

from studio_schemas.enums import DecisionType, Priority
from studio_schemas.models import NonEmptyText, RecordId, StudioModel


class CreateResearchProjectRequest(StudioModel):
    topic: NonEmptyText
    priority: Priority = Priority.NORMAL
    facets: list[str] = Field(default_factory=list)


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
