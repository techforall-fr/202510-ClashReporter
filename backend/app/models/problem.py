"""Data models for Model Coordination problems (issues)."""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ProblemStatus(str, Enum):
    """Workflow state for a problem."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ProblemPriority(str, Enum):
    """Priority levels supported by APS Problems API."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ProblemReference(BaseModel):
    """Reference attached to a problem (clash, document, etc.)."""

    type: str
    id: str
    title: Optional[str] = None
    urn: Optional[str] = None


class Problem(BaseModel):
    """Normalized representation of a problem."""

    id: str
    title: str
    description: Optional[str] = None
    status: ProblemStatus = ProblemStatus.OPEN
    priority: ProblemPriority = ProblemPriority.MEDIUM
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    references: List[ProblemReference] = []
    clash_ids: List[str] = []

    class Config:
        use_enum_values = True


class ProblemsResponse(BaseModel):
    """Wrapper for list responses."""

    problems: List[Problem]
    total: int


class ProblemCreatePayload(BaseModel):
    """Payload used to create a new problem in APS."""

    title: str
    description: Optional[str] = None
    status: ProblemStatus = ProblemStatus.OPEN
    priority: ProblemPriority = ProblemPriority.MEDIUM
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None
    clash_id: str


class ProblemLinkPayload(BaseModel):
    """Payload for linking/unlinking problems to clashes."""

    clash_id: str
