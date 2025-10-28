"""Autodesk Platform Services OAuth 2.0 authentication."""
from datetime import datetime, timedelta
from typing import Optional

import httpx

from app.core.config import settings
from app.core.logging import get_logger, log_api_call, mask_secret

logger = get_logger(__name__)


class APSToken:
    """APS access token with expiration tracking."""
    
    def __init__(self, access_token: str, expires_in: int, refresh_token: Optional[str] = None):
        self.access_token = access_token
        self.expires_at = datetime.now() + timedelta(seconds=expires_in - 60)  # 60s buffer
        self.refresh_token = refresh_token
    
    def is_valid(self) -> bool:
        """Check if token is still valid."""
        return datetime.now() < self.expires_at


class APSAuthClient:
    """Client for APS OAuth 2.0 authentication."""
    
    def __init__(self):
        self.client_id = settings.aps_client_id
        self.client_secret = settings.aps_client_secret
        self.auth_url = settings.aps_auth_url
        self._token: Optional[APSToken] = None  # 2-legged token (fallback)
        self._user_token: Optional[APSToken] = None  # 3-legged token (preferred)
    
    async def get_token(self, scopes: Optional[list[str]] = None) -> str:
        """
        Get a valid access token, refreshing if needed.
        
        ALWAYS prefers 3-legged token if available, falls back to 2-legged.
        
        Args:
            scopes: List of OAuth scopes. Defaults to data:read and viewables:read
            
        Returns:
            Valid access token string
            
        Raises:
            httpx.HTTPError: If authentication fails
        """
        # ALWAYS check for 3-legged token first (even if 2-legged is cached)
        if self._user_token:
            if self._user_token.is_valid():
                logger.debug("✅ Using 3-legged user token (authenticated)")
                return self._user_token.access_token
            elif self._user_token.refresh_token:
                logger.info("3-legged token expired, refreshing...")
                return await self.refresh_user_token()
            else:
                # 3-legged token expired and no refresh token
                logger.warning("3-legged token expired without refresh token, clearing it")
                self._user_token = None
        
        # No 3-legged token available, fall back to 2-legged
        # Check cached 2-legged token
        if self._token and self._token.is_valid():
            logger.debug("⚠️ Using 2-legged token (fallback - user not authenticated)")
            return self._token.access_token
        
        # Request new token
        logger.info("Requesting new APS token")
        if scopes is None:
            scopes = ["data:read", "viewables:read", "account:read", "data:create"]
        
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
                f"2-legged token obtained successfully. "
                f"Expires in {expires_in}s. "
                f"Token: {mask_secret(access_token, 8)}"
            )
            
            self._token = APSToken(access_token, expires_in)
            return self._token.access_token
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        """
        Exchange authorization code for access token (3-legged OAuth).
        
        Args:
            code: Authorization code received from callback
            redirect_uri: The same redirect URI used in the authorization request
            
        Returns:
            Token data including access_token and refresh_token
        """
        logger.info("Exchanging authorization code for 3-legged token")
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri
        }
        
        log_api_call(logger, "POST", self.auth_url)
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(self.auth_url, data=data)
            response.raise_for_status()
            
            result = response.json()
            access_token = result["access_token"]
            refresh_token = result.get("refresh_token")
            expires_in = result["expires_in"]
            
            logger.info(
                f"3-legged token obtained successfully. "
                f"Expires in {expires_in}s. "
                f"Token: {mask_secret(access_token, 8)}"
            )
            
            # Store the 3-legged token
            self._user_token = APSToken(access_token, expires_in, refresh_token)
            
            return result
    
    async def refresh_user_token(self) -> str:
        """
        Refresh the 3-legged user token using refresh token.
        
        Returns:
            New access token string
        """
        if not self._user_token or not self._user_token.refresh_token:
            raise ValueError("No refresh token available")
        
        logger.info("Refreshing 3-legged user token")
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self._user_token.refresh_token
        }
        
        log_api_call(logger, "POST", self.auth_url)
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(self.auth_url, data=data)
            response.raise_for_status()
            
            result = response.json()
            access_token = result["access_token"]
            refresh_token = result.get("refresh_token", self._user_token.refresh_token)
            expires_in = result["expires_in"]
            
            logger.info(
                f"Token refreshed successfully. "
                f"Expires in {expires_in}s. "
                f"Token: {mask_secret(access_token, 8)}"
            )
            
            self._user_token = APSToken(access_token, expires_in, refresh_token)
            return self._user_token.access_token
    
    def has_user_token(self) -> bool:
        """Check if a 3-legged user token is available."""
        return self._user_token is not None and self._user_token.is_valid()
    
    def clear_user_token(self):
        """Clear the stored 3-legged user token (logout)."""
        logger.info("Clearing 3-legged user token")
        self._user_token = None
    
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
