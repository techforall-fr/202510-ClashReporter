"""Clash data service with filtering and sorting."""
from typing import List, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.mock.generate import get_mock_clashes
from app.models.clash import Clash, ClashFilter, ClashesResponse, ClashSeverity, ClashStatus
from app.services.aps_mc_client import get_mc_client

logger = get_logger(__name__)


class ClashService:
    """Service for managing clash data."""
    
    def __init__(self):
        self._clashes_cache: Optional[List[Clash]] = None
    
    async def get_all_clashes(self, force_refresh: bool = False) -> List[Clash]:
        """Get all clashes, using cache when possible."""
        if self._clashes_cache is not None and not force_refresh:
            logger.debug("Returning cached clashes")
            return self._clashes_cache
        
        if settings.is_mock_mode:
            logger.info("Using mock clashes (mock mode enabled)")
            self._clashes_cache = get_mock_clashes()
        else:
            logger.info("Fetching clashes from APS")
            try:
                mc_client = get_mc_client()
                self._clashes_cache = await mc_client.fetch_all_clashes()
            except Exception as e:
                logger.error(f"Failed to fetch from APS, falling back to mock: {e}")
                self._clashes_cache = get_mock_clashes()
        
        return self._clashes_cache
    
    def _apply_filters(self, clashes: List[Clash], filters: ClashFilter) -> List[Clash]:
        """Apply filters to clash list."""
        filtered = clashes
        
        # Filter by severity
        if filters.severity:
            filtered = [c for c in filtered if c.severity in filters.severity]
        
        # Filter by status
        if filters.status:
            filtered = [c for c in filtered if c.status in filters.status]
        
        # Filter by discipline
        if filters.discipline:
            disc = filters.discipline.lower()
            filtered = [
                c for c in filtered 
                if disc in c.discipline_a.lower() or disc in c.discipline_b.lower()
            ]
        
        # Filter by level
        if filters.level:
            filtered = [c for c in filtered if c.location.level == filters.level]
        
        return filtered
    
    def _sort_clashes(self, clashes: List[Clash], sort_by: str, sort_order: str) -> List[Clash]:
        """Sort clashes by specified field."""
        reverse = sort_order.lower() == "desc"
        
        if sort_by == "severity":
            severity_order = {ClashSeverity.HIGH: 0, ClashSeverity.MEDIUM: 1, ClashSeverity.LOW: 2}
            clashes.sort(key=lambda c: severity_order[c.severity], reverse=not reverse)
        elif sort_by == "status":
            status_order = {ClashStatus.OPEN: 0, ClashStatus.RESOLVED: 1, ClashStatus.SUPPRESSED: 2}
            clashes.sort(key=lambda c: status_order[c.status], reverse=reverse)
        elif sort_by == "updated_at":
            clashes.sort(key=lambda c: c.updated_at, reverse=reverse)
        elif sort_by == "created_at":
            clashes.sort(key=lambda c: c.created_at, reverse=reverse)
        
        return clashes
    
    async def query_clashes(self, filters: ClashFilter) -> ClashesResponse:
        """Query clashes with filtering, sorting, and pagination."""
        # Get all clashes
        all_clashes = await self.get_all_clashes()
        
        # Apply filters
        filtered = self._apply_filters(all_clashes, filters)
        
        # Sort
        sorted_clashes = self._sort_clashes(filtered, filters.sort_by, filters.sort_order)
        
        # Paginate
        total = len(sorted_clashes)
        total_pages = (total + filters.page_size - 1) // filters.page_size
        
        start_idx = (filters.page - 1) * filters.page_size
        end_idx = start_idx + filters.page_size
        page_clashes = sorted_clashes[start_idx:end_idx]
        
        return ClashesResponse(
            clashes=page_clashes,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=total_pages
        )
    
    async def get_clash_by_id(self, clash_id: str) -> Optional[Clash]:
        """Get a specific clash by ID."""
        all_clashes = await self.get_all_clashes()
        for clash in all_clashes:
            if clash.id == clash_id:
                return clash
        return None


# Global service instance
_clash_service: Optional[ClashService] = None


def get_clash_service() -> ClashService:
    """Get or create the global clash service."""
    global _clash_service
    if _clash_service is None:
        _clash_service = ClashService()
    return _clash_service
