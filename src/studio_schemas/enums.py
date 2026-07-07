from enum import StrEnum


class ActivityEventType(StrEnum):
    ARTIFACT_CREATED = "artifact_created"
    DECISION_RECORDED = "decision_recorded"
    EVIDENCE_ATTACHED = "evidence_attached"
    PROJECT_CREATED = "project_created"
    PROPOSAL_CREATED = "proposal_created"
    TASK_COMPLETED = "task_completed"
    TASK_CREATED = "task_created"
    TASK_FAILED = "task_failed"
    TASK_STARTED = "task_started"
    THESIS_CREATED = "thesis_created"


class DecisionType(StrEnum):
    APPROVED = "approved"
    REJECTED = "rejected"


class Desk(StrEnum):
    FUNDAMENTAL = "fundamental"
    INDUSTRY = "industry"
    MACRO_POLICY = "macro_policy"


class EvidenceSourceType(StrEnum):
    ARTICLE = "article"
    FIXTURE = "fixture"
    NOTE = "note"
    PDF = "pdf"
    TRANSCRIPT = "transcript"


class Priority(StrEnum):
    HIGH = "high"
    LOW = "low"
    NORMAL = "normal"


class ProjectStatus(StrEnum):
    CREATED = "created"
    COMPLETED = "completed"
    FAILED = "failed"
    PLANNING = "planning"
    RUNNING = "running"


class ProposalAction(StrEnum):
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    WATCHLIST = "watchlist"


class ProposalConviction(StrEnum):
    HIGH = "high"
    LOW = "low"
    MEDIUM = "medium"


class ProposalStatus(StrEnum):
    APPROVED = "approved"
    PENDING_REVIEW = "pending_review"
    REJECTED = "rejected"


class TaskStatus(StrEnum):
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"


class ThesisStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DRAFT = "draft"
    SUPERSEDED = "superseded"
