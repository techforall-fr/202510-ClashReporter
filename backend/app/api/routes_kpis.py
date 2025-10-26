"""KPI-related API routes."""
from fastapi import APIRouter

from app.models.kpis import KPIs
from app.services.clashes import get_clash_service
from app.services.kpis import calculate_kpis

router = APIRouter(prefix="/api/kpis", tags=["kpis"])


@router.get("", response_model=KPIs)
async def get_kpis():
    """
    Get calculated KPIs for all clashes.
    
    Returns aggregated metrics including:
    - Total clashes
    - Distribution by severity
    - Distribution by status
    - Resolved percentage
    - Top categories
    - Discipline statistics
    - Level statistics
    """
    clash_service = get_clash_service()
    clashes = await clash_service.get_all_clashes()
    kpis = calculate_kpis(clashes)
    return kpis
