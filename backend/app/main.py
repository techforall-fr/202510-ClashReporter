"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_auth import router as auth_router
from app.api.routes_clashes import router as clashes_router
from app.api.routes_kpis import router as kpis_router
from app.api.routes_report import router as report_router
from app.api.routes_tokens import router as tokens_router
from app.api.routes_viewer import router as viewer_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Smart Clash Reporter API",
    description="API pour la coordination de modèles BIM et génération de rapports de clashes",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(clashes_router)
app.include_router(kpis_router)
app.include_router(tokens_router)
app.include_router(report_router)
app.include_router(viewer_router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "mode": "mock" if settings.is_mock_mode else "live"
    }


@app.get("/api/config")
async def get_config():
    """Get public configuration information."""
    return {
        "is_mock_mode": settings.is_mock_mode,
        "has_aps_credentials": settings.has_aps_credentials,
        "project_id": settings.aps_project_id if not settings.is_mock_mode else None,
        "api_version": "1.0.0"
    }


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("=" * 60)
    logger.info("Smart Clash Reporter API Starting")
    logger.info("=" * 60)
    logger.info(f"Mode: {'MOCK' if settings.is_mock_mode else 'LIVE'}")
    logger.info(f"USE_MOCK setting: {settings.use_mock}")
    logger.info(f"APS Credentials: {'Configured' if settings.has_aps_credentials else 'Not configured'}")
    
    # Warning if LIVE mode without credentials
    if not settings.is_mock_mode and not settings.has_aps_credentials:
        logger.warning("⚠️  LIVE mode enabled but APS credentials are missing or incomplete!")
        logger.warning("⚠️  The application will attempt to connect to APS but may fail.")
        logger.warning("⚠️  Required credentials: APS_CLIENT_ID, APS_CLIENT_SECRET, APS_ACCOUNT_ID, APS_PROJECT_ID")
    
    if settings.has_aps_credentials and not settings.is_mock_mode:
        logger.info(f"APS Project ID: {settings.aps_project_id}")
        logger.info(f"APS Account ID: {settings.aps_account_id}")
    
    logger.info(f"CORS Origins: {settings.cors_origins_list}")
    logger.info(f"Exports Directory: {settings.exports_dir}")
    logger.info(f"Captures Directory: {settings.captures_dir}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Smart Clash Reporter API Shutting Down")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
