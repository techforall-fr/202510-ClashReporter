"""KPI calculation service."""
from collections import Counter, defaultdict
from datetime import datetime
from typing import List

from app.models.clash import Clash, ClashSeverity, ClashStatus
from app.models.kpis import (
    CategoryCount,
    DisciplineStats,
    KPIs,
    SeverityCount,
    StatusCount,
)


def calculate_kpis(clashes: List[Clash]) -> KPIs:
    """Calculate KPIs from clash list."""
    total = len(clashes)
    
    if total == 0:
        return KPIs(last_updated=datetime.now().isoformat())
    
    # Count by severity
    severity_counts = Counter(c.severity for c in clashes)
    by_severity = SeverityCount(
        high=severity_counts.get(ClashSeverity.HIGH, 0),
        medium=severity_counts.get(ClashSeverity.MEDIUM, 0),
        low=severity_counts.get(ClashSeverity.LOW, 0)
    )
    
    # Count by status
    status_counts = Counter(c.status for c in clashes)
    by_status = StatusCount(
        open=status_counts.get(ClashStatus.OPEN, 0),
        resolved=status_counts.get(ClashStatus.RESOLVED, 0),
        suppressed=status_counts.get(ClashStatus.SUPPRESSED, 0)
    )
    
    # Resolved percentage
    resolved_pct = (by_status.resolved / total * 100) if total > 0 else 0.0
    
    # Top categories
    category_counter = Counter()
    for clash in clashes:
        category_counter[clash.element_a.category] += 1
        category_counter[clash.element_b.category] += 1
    
    top_categories = [
        CategoryCount(category=cat, count=count)
        for cat, count in category_counter.most_common(5)
    ]
    
    # By discipline pair
    discipline_stats: dict = defaultdict(lambda: {"count": 0, "high": 0, "medium": 0, "low": 0})
    for clash in clashes:
        # Create normalized discipline pair (alphabetically sorted)
        pair = tuple(sorted([clash.discipline_a, clash.discipline_b]))
        key = f"{pair[0]} vs {pair[1]}"
        
        discipline_stats[key]["count"] += 1
        if clash.severity == ClashSeverity.HIGH:
            discipline_stats[key]["high"] += 1
        elif clash.severity == ClashSeverity.MEDIUM:
            discipline_stats[key]["medium"] += 1
        else:
            discipline_stats[key]["low"] += 1
    
    by_discipline = [
        DisciplineStats(
            discipline_pair=pair,
            count=stats["count"],
            high=stats["high"],
            medium=stats["medium"],
            low=stats["low"]
        )
        for pair, stats in sorted(
            discipline_stats.items(), 
            key=lambda x: x[1]["count"], 
            reverse=True
        )
    ]
    
    # By level
    level_counter = Counter(c.location.level for c in clashes if c.location.level)
    by_level = dict(level_counter)
    
    return KPIs(
        total_clashes=total,
        by_severity=by_severity,
        by_status=by_status,
        resolved_percentage=round(resolved_pct, 1),
        top_categories=top_categories,
        by_discipline=by_discipline,
        by_level=by_level,
        last_updated=datetime.now().isoformat()
    )
