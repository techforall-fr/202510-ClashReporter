"""Data models for clash objects."""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ClashStatus(str, Enum):
    """Clash status enumeration."""
    OPEN = "open"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class ClashSeverity(str, Enum):
    """Clash severity enumeration."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Location(BaseModel):
    """3D location data."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    level: Optional[str] = None


class Element(BaseModel):
    """BIM element information."""
    urn: str
    guid: str
    name: str = ""
    category: str = ""


class Clash(BaseModel):
    """Normalized clash data model."""
    id: str
    group_id: str
    title: str
    status: ClashStatus = ClashStatus.OPEN
    severity: ClashSeverity = ClashSeverity.MEDIUM
    discipline_a: str = ""
    discipline_b: str = ""
    element_a: Element
    element_b: Element
    location: Location
    screenshot_url: Optional[str] = None
    acc_link: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class ClashFilter(BaseModel):
    """Filter parameters for clash queries."""
    severity: Optional[list[ClashSeverity]] = None
    status: Optional[list[ClashStatus]] = None
    discipline: Optional[str] = None
    level: Optional[str] = None
    sort_by: str = "severity"
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 50


class ClashesResponse(BaseModel):
    """Paginated clash response."""
    clashes: list[Clash]
    total: int
    page: int
    page_size: int
    total_pages: int
