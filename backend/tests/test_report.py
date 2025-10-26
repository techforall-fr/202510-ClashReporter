"""Tests for PDF report generation."""
import pytest

from app.mock.generate import get_mock_clashes
from app.models.kpis import ReportConfig
from app.services.kpis import calculate_kpis
from app.services.report_pdf import get_pdf_generator


def test_pdf_generation():
    """Test that PDF generation produces valid output."""
    # Get mock data
    clashes = get_mock_clashes()[:20]  # Use subset for faster test
    kpis = calculate_kpis(clashes)
    
    # Create config
    config = ReportConfig(
        title="Test Report",
        prepared_by="Pytest",
        include_screenshots=False
    )
    
    # Generate PDF
    generator = get_pdf_generator()
    pdf_bytes = generator.generate_report(kpis, clashes, config)
    
    # Basic validation
    assert pdf_bytes is not None
    assert len(pdf_bytes) > 0
    
    # Check PDF header (should start with %PDF)
    assert pdf_bytes[:4] == b'%PDF'
    
    # Check minimum size (should be substantial)
    assert len(pdf_bytes) > 50000  # At least 50KB


def test_pdf_with_empty_clashes():
    """Test PDF generation with no clashes."""
    clashes = []
    kpis = calculate_kpis(clashes)
    
    config = ReportConfig(
        title="Empty Report",
        prepared_by="Pytest"
    )
    
    generator = get_pdf_generator()
    pdf_bytes = generator.generate_report(kpis, clashes, config)
    
    # Should still generate a valid PDF
    assert pdf_bytes is not None
    assert pdf_bytes[:4] == b'%PDF'


def test_pdf_contains_sections():
    """Test that PDF contains expected sections."""
    clashes = get_mock_clashes()[:10]
    kpis = calculate_kpis(clashes)
    
    config = ReportConfig(
        title="Section Test Report",
        prepared_by="Pytest"
    )
    
    generator = get_pdf_generator()
    pdf_bytes = generator.generate_report(kpis, clashes, config)
    
    # Convert to string to search for content
    pdf_str = pdf_bytes.decode('latin-1', errors='ignore')
    
    # Check for key sections (these are embedded as text in PDF)
    assert "Section Test Report" in pdf_str or "Test Report" in pdf_str
    assert "Smart Clash Reporter" in pdf_str
