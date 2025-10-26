"""Clash-related API routes."""
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.clash import Clash, ClashFilter, ClashesResponse, ClashSeverity, ClashStatus
from app.services.clashes import get_clash_service

router = APIRouter(prefix="/api/clashes", tags=["clashes"])


@router.get("", response_model=ClashesResponse)
async def get_clashes(
    severity: Optional[List[ClashSeverity]] = Query(None),
    status: Optional[List[ClashStatus]] = Query(None),
    discipline: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    sort_by: str = Query("severity", regex="^(severity|status|updated_at|created_at)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200)
):
    """
    Get clashes with filtering, sorting, and pagination.
    
    Query parameters:
    - severity: Filter by severity (can specify multiple)
    - status: Filter by status (can specify multiple)
    - discipline: Filter by discipline (partial match)
    - level: Filter by level (exact match)
    - sort_by: Field to sort by
    - sort_order: Sort order (asc/desc)
    - page: Page number (1-indexed)
    - page_size: Items per page
    """
    clash_filter = ClashFilter(
        severity=severity,
        status=status,
        discipline=discipline,
        level=level,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size
    )
    
    clash_service = get_clash_service()
    return await clash_service.query_clashes(clash_filter)


@router.get("/{clash_id}", response_model=Clash)
async def get_clash_by_id(clash_id: str):
    """Get a specific clash by ID."""
    clash_service = get_clash_service()
    clash = await clash_service.get_clash_by_id(clash_id)
    
    if not clash:
        raise HTTPException(status_code=404, detail=f"Clash {clash_id} not found")
    
    return clash
