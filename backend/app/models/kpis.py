"""Data models for KPIs and metrics."""
from typing import Dict, List

from pydantic import BaseModel


class SeverityCount(BaseModel):
    """Count of clashes by severity."""
    high: int = 0
    medium: int = 0
    low: int = 0


class StatusCount(BaseModel):
    """Count of clashes by status."""
    open: int = 0
    resolved: int = 0
    suppressed: int = 0


class CategoryCount(BaseModel):
    """Category with count."""
    category: str
    count: int


class DisciplineStats(BaseModel):
    """Statistics by discipline pair."""
    discipline_pair: str
    count: int
    high: int = 0
    medium: int = 0
    low: int = 0


class KPIs(BaseModel):
    """Key performance indicators for clashes."""
    total_clashes: int = 0
    by_severity: SeverityCount = SeverityCount()
    by_status: StatusCount = StatusCount()
    resolved_percentage: float = 0.0
    top_categories: List[CategoryCount] = []
    by_discipline: List[DisciplineStats] = []
    by_level: Dict[str, int] = {}
    last_updated: str = ""


class ReportConfig(BaseModel):
    """Configuration for PDF report generation."""
    filters: Dict = {}
    title: str = "Clash Report"
    prepared_by: str = "Smart Clash Reporter"
    logo_path: str = ""
    include_screenshots: bool = True
