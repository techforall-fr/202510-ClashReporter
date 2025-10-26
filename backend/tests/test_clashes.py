"""Tests for clash service."""
import pytest

from app.models.clash import Clash, ClashFilter, ClashSeverity, ClashStatus
from app.services.clashes import ClashService
from app.services.kpis import calculate_kpis


@pytest.fixture
def clash_service():
    """Create clash service instance."""
    return ClashService()


@pytest.mark.asyncio
async def test_get_all_clashes(clash_service):
    """Test fetching all clashes."""
    clashes = await clash_service.get_all_clashes()
    
    assert clashes is not None
    assert len(clashes) > 0
    assert isinstance(clashes[0], Clash)


@pytest.mark.asyncio
async def test_query_clashes_with_filters(clash_service):
    """Test querying clashes with filters."""
    # Filter by high severity
    filters = ClashFilter(
        severity=[ClashSeverity.HIGH],
        page=1,
        page_size=10
    )
    
    result = await clash_service.query_clashes(filters)
    
    assert result.total > 0
    assert len(result.clashes) <= 10
    
    # Verify all returned clashes are high severity
    for clash in result.clashes:
        assert clash.severity == ClashSeverity.HIGH


@pytest.mark.asyncio
async def test_query_clashes_pagination(clash_service):
    """Test pagination works correctly."""
    filters = ClashFilter(page=1, page_size=10)
    page1 = await clash_service.query_clashes(filters)
    
    filters.page = 2
    page2 = await clash_service.query_clashes(filters)
    
    # Should have different clashes on different pages
    page1_ids = {c.id for c in page1.clashes}
    page2_ids = {c.id for c in page2.clashes}
    
    assert page1_ids != page2_ids


@pytest.mark.asyncio
async def test_get_clash_by_id(clash_service):
    """Test fetching a specific clash by ID."""
    # Get all clashes first
    all_clashes = await clash_service.get_all_clashes()
    test_id = all_clashes[0].id
    
    # Fetch by ID
    clash = await clash_service.get_clash_by_id(test_id)
    
    assert clash is not None
    assert clash.id == test_id


@pytest.mark.asyncio
async def test_get_nonexistent_clash(clash_service):
    """Test fetching a non-existent clash returns None."""
    clash = await clash_service.get_clash_by_id("nonexistent_id_12345")
    assert clash is None


def test_calculate_kpis():
    """Test KPI calculation."""
    from app.mock.generate import get_mock_clashes
    
    clashes = get_mock_clashes()
    kpis = calculate_kpis(clashes)
    
    # Basic assertions
    assert kpis.total_clashes == len(clashes)
    assert kpis.by_severity.high >= 0
    assert kpis.by_severity.medium >= 0
    assert kpis.by_severity.low >= 0
    assert kpis.by_status.open >= 0
    assert kpis.by_status.resolved >= 0
    assert 0 <= kpis.resolved_percentage <= 100
    
    # Check totals match
    severity_total = kpis.by_severity.high + kpis.by_severity.medium + kpis.by_severity.low
    assert severity_total == kpis.total_clashes


def test_kpis_top_categories():
    """Test that top categories are calculated correctly."""
    from app.mock.generate import get_mock_clashes
    
    clashes = get_mock_clashes()
    kpis = calculate_kpis(clashes)
    
    # Should have top categories
    assert len(kpis.top_categories) > 0
    assert len(kpis.top_categories) <= 5
    
    # Check ordering (should be descending by count)
    counts = [cat.count for cat in kpis.top_categories]
    assert counts == sorted(counts, reverse=True)
