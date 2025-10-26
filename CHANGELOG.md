# Changelog

All notable changes to Smart Clash Reporter will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-26

### 🎉 Initial Release

#### Added
- **Backend API (FastAPI)**
  - REST API with Swagger documentation
  - Autodesk Platform Services (APS) authentication
  - Model Coordination API client
  - Clash data service with filtering and pagination
  - KPI calculation service
  - PDF report generation with charts
  - Screenshot capture storage
  - Health check and configuration endpoints

- **Frontend (Streamlit)**
  - Dashboard with KPI cards and charts
  - Clash table with filtering (severity, status, discipline, level)
  - PDF report generation UI
  - CSV export functionality
  - Responsive design with custom CSS
  - Autodesk Viewer placeholder

- **Mock Mode**
  - Complete mock data system (100 clashes)
  - Realistic BIM data generation
  - Auto-activation when no credentials
  - Demo URN for viewer

- **PDF Reports**
  - Cover page with metadata
  - KPI summary section with charts (bar, pie, horizontal bar)
  - Detailed clash tables grouped by severity
  - Screenshot integration
  - ACC links for each clash
  - Professional styling with ReportLab

- **Developer Tools**
  - Comprehensive test suite (pytest)
  - Type checking (mypy)
  - Code formatting (black, ruff)
  - Makefile for common tasks
  - Demo launcher script
  - Quick start scripts (PowerShell & Bash)

- **Documentation**
  - Comprehensive README with installation guide
  - Quick start guide (QUICKSTART.md)
  - Demo storyboard (DEMO.md)
  - Contributing guidelines (CONTRIBUTING.md)
  - API documentation (Swagger/ReDoc)

- **Deployment**
  - Docker support (Dockerfile + docker-compose)
  - Environment configuration (.env.sample)
  - CORS configuration
  - Production-ready logging

#### Features by Category

**Clash Management:**
- Fetch clashes from APS Model Coordination
- Filter by severity (high/medium/low)
- Filter by status (open/resolved/suppressed)
- Filter by discipline (partial match)
- Filter by level (exact match)
- Sort by severity, status, or date
- Pagination support (up to 200 items/page)

**Analytics:**
- Total clash count
- Distribution by severity
- Distribution by status
- Resolved percentage
- Top 5 element categories
- Clash count by discipline pairs
- Distribution by building level

**Reporting:**
- Automated PDF generation
- Custom report title and author
- Filtering applied to reports
- Chart generation (matplotlib)
- Screenshot inclusion
- Metadata and timestamps
- Professional layout

**Integration:**
- OAuth 2.0 with APS
- Model Coordination API
- Autodesk Viewer (token support)
- ACC deep links

#### Technical Specs

**Backend:**
- Python 3.11+
- FastAPI 0.109+
- Pydantic for validation
- ReportLab for PDF
- Matplotlib for charts
- Async/await support

**Frontend:**
- Streamlit 1.30+
- Plotly for visualizations
- Pandas for data manipulation
- Responsive HTML/CSS

**Testing:**
- pytest with async support
- 70%+ code coverage
- Unit tests for core logic
- PDF validation tests

---

## [Unreleased]

### Planned Features
- [ ] Enhanced viewer integration (focus/isolate)
- [ ] Real-time screenshot capture from viewer
- [ ] Excel export with formatting
- [ ] Multi-model support
- [ ] User authentication
- [ ] Clash history tracking
- [ ] Email notifications
- [ ] Clash assignment workflow

### Known Issues
- Viewer integration requires manual JavaScript setup
- MCP API endpoints may need adjustment per APS version
- Large clash sets (>1000) may impact PDF generation time
- No persistent database (cache in memory only)

---

## Version History

- **1.0.0** (2025-10-26) - Initial release with core features
- **0.9.0** (2025-10-20) - Beta release for testing
- **0.1.0** (2025-10-15) - Alpha prototype

---

## Migration Guides

### From Beta (0.9.0) to 1.0.0

No breaking changes. Simply update dependencies:

```bash
cd backend
pip install -r requirements.txt --upgrade
cd ../frontend
pip install -r requirements.txt --upgrade
```

---

For detailed changes and commit history, see the [GitHub repository](https://github.com/your-repo/smart-clash-reporter).
