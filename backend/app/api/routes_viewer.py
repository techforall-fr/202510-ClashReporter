"""API routes for Autodesk Viewer integration."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.core.logging import get_logger
from app.services.aps_auth import get_auth_client
from app.services.clashes import get_clash_service

logger = get_logger(__name__)
router = APIRouter(prefix="/api/viewer", tags=["viewer"])


@router.get("/token")
async def get_viewer_token():
    """
    Get an access token for the Autodesk Viewer.
    
    Returns a 2-legged OAuth token with viewables:read scope.
    """
    try:
        auth_client = get_auth_client()
        token = await auth_client.get_token()
        
        return {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": 3600
        }
    except Exception as e:
        logger.error(f"Error getting viewer token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-urns")
async def get_model_urns():
    """
    Get unique model URNs from current clashes.
    
    Returns a list of document URNs that need to be loaded in the viewer.
    """
    try:
        clash_service = get_clash_service()
        clashes = await clash_service.get_all_clashes()
        
        # Extract unique URNs
        urns = set()
        for clash in clashes:
            if clash.element_a.urn:
                urns.add(clash.element_a.urn)
            if clash.element_b.urn:
                urns.add(clash.element_b.urn)
        
        return {
            "urns": list(urns),
            "count": len(urns)
        }
    except Exception as e:
        logger.error(f"Error getting model URNs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clash/{clash_id}")
async def get_clash_viewer_data(clash_id: str):
    """
    Get viewer-specific data for a clash (URNs, object IDs, etc.).
    
    Used to focus/zoom on a specific clash in the viewer.
    """
    try:
        clash_service = get_clash_service()
        clashes = await clash_service.get_all_clashes()
        
        # Find the specific clash
        clash = next((c for c in clashes if c.id == clash_id), None)
        
        if not clash:
            raise HTTPException(status_code=404, detail="Clash not found")
        
        return {
            "clash_id": clash.id,
            "element_a": {
                "urn": clash.element_a.urn,
                "guid": clash.element_a.guid,
                "name": clash.element_a.name
            },
            "element_b": {
                "urn": clash.element_b.urn,
                "guid": clash.element_b.guid,
                "name": clash.element_b.name
            },
            "location": {
                "x": clash.location.x,
                "y": clash.location.y,
                "z": clash.location.z
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting clash viewer data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
