"""PDF report generation service."""
import io
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.core.logging import get_logger
from app.models.clash import Clash, ClashSeverity
from app.models.kpis import KPIs, ReportConfig
from app.services.chart_kpis import (
    create_discipline_chart,
    create_severity_chart,
    create_status_chart,
)
from app.services.storage import get_storage_service

logger = get_logger(__name__)


class PDFReportGenerator:
    """PDF report generator for clash data."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.storage = get_storage_service()
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=12
        )
    
    def _create_cover_page(self, config: ReportConfig) -> List:
        """Create cover page elements."""
        elements = []
        
        # Title
        title = Paragraph(config.title, self.title_style)
        elements.append(title)
        elements.append(Spacer(1, 1*cm))
        
        # Logo if provided
        if config.logo_path and Path(config.logo_path).exists():
            try:
                logo = Image(config.logo_path, width=8*cm, height=4*cm, kind='proportional')
                elements.append(logo)
                elements.append(Spacer(1, 1*cm))
            except Exception as e:
                logger.warning(f"Could not add logo: {e}")
        
        # Metadata
        meta_style = self.styles['Normal']
        meta_data = [
            f"<b>Date:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"<b>Préparé par:</b> {config.prepared_by}",
            f"<b>Généré par:</b> Smart Clash Reporter"
        ]
        
        for line in meta_data:
            elements.append(Paragraph(line, meta_style))
            elements.append(Spacer(1, 0.3*cm))
        
        elements.append(PageBreak())
        return elements
    
    def _create_kpi_section(self, kpis: KPIs) -> List:
        """Create KPI summary section with charts."""
        elements = []
        
        # Section header
        elements.append(Paragraph("Indicateurs clés (KPIs)", self.heading_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Summary table
        summary_data = [
            ['Indicateur', 'Valeur'],
            ['Total de clashes', str(kpis.total_clashes)],
            ['Haute sévérité', str(kpis.by_severity.high)],
            ['Moyenne sévérité', str(kpis.by_severity.medium)],
            ['Basse sévérité', str(kpis.by_severity.low)],
            ['Clashes ouverts', str(kpis.by_status.open)],
            ['Clashes résolus', str(kpis.by_status.resolved)],
            ['% Résolus', f"{kpis.resolved_percentage}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[10*cm, 5*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 1*cm))
        
        # Charts
        try:
            # Severity chart
            severity_chart_bytes = create_severity_chart(kpis)
            severity_img = Image(io.BytesIO(severity_chart_bytes), width=12*cm, height=8*cm)
            elements.append(severity_img)
            elements.append(Spacer(1, 0.5*cm))
            
            # Status chart
            status_chart_bytes = create_status_chart(kpis)
            status_img = Image(io.BytesIO(status_chart_bytes), width=12*cm, height=8*cm)
            elements.append(status_img)
            elements.append(Spacer(1, 0.5*cm))
            
            # Discipline chart
            discipline_chart_bytes = create_discipline_chart(kpis)
            discipline_img = Image(io.BytesIO(discipline_chart_bytes), width=14*cm, height=9*cm)
            elements.append(discipline_img)
            
        except Exception as e:
            logger.error(f"Failed to generate charts: {e}")
            elements.append(Paragraph(f"Erreur lors de la génération des graphiques: {e}", self.styles['Normal']))
        
        elements.append(PageBreak())
        return elements
    
    def _create_clash_details(self, clashes: List[Clash], include_screenshots: bool = True) -> List:
        """Create detailed clash listing section."""
        elements = []
        
        # Section header
        elements.append(Paragraph("Détails des clashes", self.heading_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Group by severity
        high_clashes = [c for c in clashes if c.severity == ClashSeverity.HIGH]
        medium_clashes = [c for c in clashes if c.severity == ClashSeverity.MEDIUM]
        low_clashes = [c for c in clashes if c.severity == ClashSeverity.LOW]
        
        for severity_name, clash_group in [
            ("Haute sévérité", high_clashes),
            ("Moyenne sévérité", medium_clashes),
            ("Basse sévérité", low_clashes)
        ]:
            if not clash_group:
                continue
            
            # Subsection
            elements.append(Paragraph(f"{severity_name} ({len(clash_group)} clashes)", self.heading_style))
            elements.append(Spacer(1, 0.3*cm))
            
            # Limit to first 20 per severity to keep PDF manageable
            for clash in clash_group[:20]:
                # Clash info
                clash_data = [
                    ['ID', clash.id],
                    ['Titre', clash.title],
                    ['Statut', clash.status.value.capitalize()],
                    ['Disciplines', f"{clash.discipline_a} vs {clash.discipline_b}"],
                    ['Élément A', f"{clash.element_a.name} ({clash.element_a.category})"],
                    ['Élément B', f"{clash.element_b.name} ({clash.element_b.category})"],
                    ['Niveau', clash.location.level or 'N/A'],
                ]
                
                if clash.acc_link:
                    clash_data.append(['Lien ACC', clash.acc_link])
                
                clash_table = Table(clash_data, colWidths=[4*cm, 11*cm])
                clash_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e7ff')),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                ]))
                
                elements.append(clash_table)
                
                # Screenshot if available
                if include_screenshots:
                    capture_path = self.storage.get_capture_path(clash.id)
                    if capture_path and capture_path.exists():
                        try:
                            img = Image(str(capture_path), width=10*cm, height=6*cm, kind='proportional')
                            elements.append(Spacer(1, 0.2*cm))
                            elements.append(img)
                        except Exception as e:
                            logger.warning(f"Could not add screenshot for {clash.id}: {e}")
                
                elements.append(Spacer(1, 0.5*cm))
            
            if len(clash_group) > 20:
                elements.append(Paragraph(
                    f"<i>... et {len(clash_group) - 20} autres clashes de {severity_name.lower()}</i>",
                    self.styles['Italic']
                ))
            
            elements.append(Spacer(1, 0.5*cm))
        
        return elements
    
    def _add_footer(self, canvas_obj: canvas.Canvas, doc):
        """Add footer with page numbers."""
        canvas_obj.saveState()
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.grey)
        
        page_num = canvas_obj.getPageNumber()
        text = f"Smart Clash Reporter - Page {page_num}"
        canvas_obj.drawCentredString(A4[0] / 2, 1*cm, text)
        
        canvas_obj.restoreState()
    
    def generate_report(
        self, 
        kpis: KPIs, 
        clashes: List[Clash], 
        config: ReportConfig
    ) -> bytes:
        """
        Generate complete PDF report.
        
        Args:
            kpis: KPI data
            clashes: List of clashes to include
            config: Report configuration
            
        Returns:
            PDF bytes
        """
        logger.info(f"Generating PDF report with {len(clashes)} clashes")
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Build content
        story = []
        
        # Cover page
        story.extend(self._create_cover_page(config))
        
        # KPIs
        story.extend(self._create_kpi_section(kpis))
        
        # Clash details
        story.extend(self._create_clash_details(clashes, config.include_screenshots))
        
        # Footer disclaimer
        story.append(Spacer(1, 1*cm))
        disclaimer = Paragraph(
            "<i>Ce rapport a été généré automatiquement par Smart Clash Reporter. "
            "Les données proviennent d'Autodesk ACC Model Coordination.</i>",
            self.styles['Italic']
        )
        story.append(disclaimer)
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
        
        buffer.seek(0)
        pdf_bytes = buffer.read()
        
        logger.info(f"PDF report generated successfully ({len(pdf_bytes)} bytes)")
        return pdf_bytes


def get_pdf_generator() -> PDFReportGenerator:
    """Get PDF generator instance."""
    return PDFReportGenerator()
