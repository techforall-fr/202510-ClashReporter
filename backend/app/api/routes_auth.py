"""OAuth authentication routes."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.core.config import settings
from app.core.logging import get_logger
from app.services.aps_auth import get_auth_client

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = get_logger(__name__)


class AuthStatusResponse(BaseModel):
    """Authentication status response."""
    authenticated: bool
    user_token_available: bool


@router.get("/login")
async def login():
    """
    Initiate OAuth 3-legged authentication flow.
    
    Redirects user to Autodesk login page.
    """
    logger.info("Initiating OAuth 3-legged login")
    
    # Construct authorization URL
    redirect_uri = f"http://localhost:{settings.api_port}/api/auth/callback"
    
    # IMPORTANT: Use URL encoding for the redirect_uri
    from urllib.parse import quote
    redirect_uri_encoded = quote(redirect_uri, safe='')
    
    auth_url = (
        f"https://developer.api.autodesk.com/authentication/v2/authorize"
        f"?response_type=code"
        f"&client_id={settings.aps_client_id}"
        f"&redirect_uri={redirect_uri_encoded}"
        f"&scope=data:read%20data:write%20account:read%20data:create"
        f"&prompt=login"
    )
    
    logger.info(f"Authorization URL: {auth_url}")
    logger.info(f"Redirect URI: {redirect_uri}")
    logger.info(f"⚠️  IMPORTANT: Ensure this callback URL is configured in your APS app:")
    logger.info(f"   → {redirect_uri}")
    
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def callback(code: str = None, error: str = None):
    """
    OAuth callback endpoint.
    
    Receives authorization code and exchanges it for access token.
    """
    if error:
        logger.error(f"OAuth error: {error}")
        raise HTTPException(status_code=400, detail=f"Authentication error: {error}")
    
    if not code:
        logger.error("No authorization code received")
        raise HTTPException(status_code=400, detail="No authorization code received")
    
    logger.info("Received authorization code, exchanging for token")
    
    try:
        auth_client = get_auth_client()
        redirect_uri = f"http://localhost:{settings.api_port}/api/auth/callback"
        
        # Exchange code for token
        token_data = await auth_client.exchange_code_for_token(code, redirect_uri)
        
        logger.info("Successfully authenticated user")
        
        # Clear the clashes cache to force refresh with new token
        from app.services.clashes import get_clash_service
        clash_service = get_clash_service()
        clash_service._clashes_cache = None
        logger.info("🔄 Clashes cache cleared - will fetch fresh data with 3-legged token")
        
        # Redirect to frontend with success message
        frontend_url = f"http://localhost:{settings.frontend_port}?auth=success"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        logger.error(f"Failed to exchange code for token: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to complete authentication: {str(e)}"
        )


@router.get("/logout")
async def logout():
    """
    Logout endpoint.
    
    Clears the stored 3-legged user token.
    """
    logger.info("User logout")
    auth_client = get_auth_client()
    auth_client.clear_user_token()
    
    return {"message": "Logged out successfully"}


@router.get("/status", response_model=AuthStatusResponse)
async def auth_status():
    """
    Check authentication status.
    
    Returns whether user is authenticated with 3-legged token.
    """
    auth_client = get_auth_client()
    has_token = auth_client.has_user_token()
    
    return AuthStatusResponse(
        authenticated=has_token,
        user_token_available=has_token
    )
