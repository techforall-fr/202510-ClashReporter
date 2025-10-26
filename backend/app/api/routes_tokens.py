"""Token-related API routes for Autodesk Viewer."""
from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.mock.generate import DEMO_URN
from app.services.aps_auth import get_auth_client

router = APIRouter(prefix="/api/token", tags=["tokens"])


@router.get("/viewer")
async def get_viewer_token():
    """
    Get an access token for the Autodesk Viewer.
    
    In mock mode, returns a demo token and URN.
    In live mode, returns a real APS token.
    """
    if settings.is_mock_mode:
        return {
            "access_token": "DEMO_TOKEN",
            "expires_in": 3600,
            "urn": DEMO_URN,
            "is_mock": True
        }
    
    try:
        auth_client = get_auth_client()
        token = await auth_client.get_viewer_token()
        
        # Return first model URN if available (in production, this should be dynamic)
        urn = settings.aps_modelset_id or DEMO_URN
        
        return {
            "access_token": token,
            "expires_in": 3600,
            "urn": urn,
            "is_mock": False
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to obtain viewer token: {str(e)}"
        )
