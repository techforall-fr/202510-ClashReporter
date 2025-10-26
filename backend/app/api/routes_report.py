"""Report generation API routes."""
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

from app.models.clash import ClashFilter
from app.models.kpis import ReportConfig
from app.services.clashes import get_clash_service
from app.services.kpis import calculate_kpis
from app.services.report_pdf import get_pdf_generator
from app.services.storage import get_storage_service

router = APIRouter(prefix="/api/report", tags=["report"])


class CaptureRequest(BaseModel):
    """Request body for saving a capture."""
    clash_id: str
    image_data_url: str


class ReportRequest(BaseModel):
    """Request body for generating a report."""
    filters: Dict[str, Any] = {}
    title: str = "Rapport de Clashes"
    prepared_by: str = "Smart Clash Reporter"
    logo_path: str = ""
    include_screenshots: bool = True


@router.post("/capture")
async def save_capture(request: CaptureRequest):
    """
    Save a screenshot capture for a clash.
    
    Accepts a base64-encoded image data URL.
    """
    try:
        storage = get_storage_service()
        filepath = storage.save_capture(request.clash_id, request.image_data_url)
        
        return {
            "success": True,
            "clash_id": request.clash_id,
            "filepath": filepath
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save capture: {str(e)}")


@router.post("/pdf")
async def generate_pdf_report(request: ReportRequest):
    """
    Generate a PDF report with clashes and KPIs.
    
    Applies filters if provided and includes screenshots if available.
    Returns the PDF file directly.
    """
    try:
        # Get clashes with filters
        clash_service = get_clash_service()
        
        # Parse filters
        clash_filter = ClashFilter(
            severity=request.filters.get("severity"),
            status=request.filters.get("status"),
            discipline=request.filters.get("discipline"),
            level=request.filters.get("level"),
            page=1,
            page_size=1000  # Get all for report
        )
        
        response = await clash_service.query_clashes(clash_filter)
        clashes = response.clashes
        
        # Calculate KPIs
        kpis = calculate_kpis(clashes)
        
        # Generate report config
        config = ReportConfig(
            filters=request.filters,
            title=request.title,
            prepared_by=request.prepared_by,
            logo_path=request.logo_path,
            include_screenshots=request.include_screenshots
        )
        
        # Generate PDF
        pdf_generator = get_pdf_generator()
        pdf_bytes = pdf_generator.generate_report(kpis, clashes, config)
        
        # Save to storage
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"clash_report_{timestamp}.pdf"
        
        storage = get_storage_service()
        storage.save_report(filename, pdf_bytes)
        
        # Return PDF
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")


@router.get("/latest")
async def get_latest_report():
    """Download the most recently generated report."""
    storage = get_storage_service()
    latest = storage.get_latest_report()
    
    if not latest:
        raise HTTPException(status_code=404, detail="No reports found")
    
    return FileResponse(
        path=str(latest),
        media_type="application/pdf",
        filename=latest.name
    )
