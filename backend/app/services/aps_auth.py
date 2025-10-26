"""Autodesk Platform Services OAuth 2.0 authentication."""
from datetime import datetime, timedelta
from typing import Optional

import httpx

from app.core.config import settings
from app.core.logging import get_logger, log_api_call, mask_secret

logger = get_logger(__name__)


class APSToken:
    """APS access token with expiration tracking."""
    
    def __init__(self, access_token: str, expires_in: int):
        self.access_token = access_token
        self.expires_at = datetime.now() + timedelta(seconds=expires_in - 60)  # 60s buffer
    
    def is_valid(self) -> bool:
        """Check if token is still valid."""
        return datetime.now() < self.expires_at


class APSAuthClient:
    """Client for APS OAuth 2.0 authentication."""
    
    def __init__(self):
        self.client_id = settings.aps_client_id
        self.client_secret = settings.aps_client_secret
        self.auth_url = settings.aps_auth_url
        self._token: Optional[APSToken] = None
    
    async def get_token(self, scopes: Optional[list[str]] = None) -> str:
        """
        Get a valid access token, refreshing if needed.
        
        Args:
            scopes: List of OAuth scopes. Defaults to data:read and viewables:read
            
        Returns:
            Valid access token string
            
        Raises:
            httpx.HTTPError: If authentication fails
        """
        # Use cached token if still valid
        if self._token and self._token.is_valid():
            logger.debug("Using cached APS token")
            return self._token.access_token
        
        # Request new token
        logger.info("Requesting new APS token")
        if scopes is None:
            scopes = ["data:read", "viewables:read"]
        
        scope_str = " ".join(scopes)
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": scope_str
        }
        
        log_api_call(logger, "POST", self.auth_url)
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(self.auth_url, data=data)
            response.raise_for_status()
            
            result = response.json()
            access_token = result["access_token"]
            expires_in = result["expires_in"]
            
            logger.info(
                f"APS token obtained successfully. "
                f"Expires in {expires_in}s. "
                f"Token: {mask_secret(access_token, 8)}"
            )
            
            self._token = APSToken(access_token, expires_in)
            return self._token.access_token
    
    async def get_viewer_token(self) -> str:
        """Get a token specifically for Autodesk Viewer."""
        return await self.get_token(scopes=["viewables:read"])


# Global auth client instance
_auth_client: Optional[APSAuthClient] = None


def get_auth_client() -> APSAuthClient:
    """Get or create the global auth client."""
    global _auth_client
    if _auth_client is None:
        _auth_client = APSAuthClient()
    return _auth_client
