"""Autodesk Platform Services Model Coordination client.

NOTE: Some endpoints are based on APS Model Coordination API documentation.
If specific endpoints differ, adjust accordingly. This implementation provides
a solid structure with mock fallback.

References:
- https://aps.autodesk.com/en/docs/acc/v1/overview/
- Model Coordination API endpoints (check latest docs)
"""
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.core.logging import get_logger, log_api_call
from app.models.clash import Clash, ClashSeverity, ClashStatus, Element, Location
from app.services.aps_auth import get_auth_client

logger = get_logger(__name__)


class APSMCClient:
    """Client for APS Model Coordination API."""
    
    def __init__(self):
        self.base_url = settings.aps_base_url
        self.account_id = settings.aps_account_id
        self.project_id = settings.aps_project_id
        self.coordination_space_id = settings.aps_coordination_space_id
        self.modelset_id = settings.aps_modelset_id
        self.auth_client = get_auth_client()
    
    async def _get_headers(self) -> Dict[str, str]:
        """Get headers with auth token."""
        token = await self.auth_client.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    async def list_model_sets(self) -> List[Dict[str, Any]]:
        """
        List all model sets in the container.
        
        GET https://developer.api.autodesk.com/bim360/modelset/v3/containers/:containerId/modelsets
        """
        url = (
            f"{self.base_url}/bim360/modelset/v3/"
            f"containers/{self.project_id}/modelsets"
        )
        
        headers = await self._get_headers()
        log_api_call(logger, "GET", url)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get("results", [])
    
    async def list_clash_tests(self, modelset_id: str = None) -> List[Dict[str, Any]]:
        """
        List clash tests for a model set.
        
        GET https://developer.api.autodesk.com/bim360/clash/v3/containers/:containerId/modelsets/:modelSetId/tests
        """
        # Use provided modelset_id or fall back to configured one
        ms_id = modelset_id or self.modelset_id
        
        url = (
            f"{self.base_url}/bim360/clash/v3/"
            f"containers/{self.project_id}/modelsets/{ms_id}/tests"
        )
        
        headers = await self._get_headers()
        log_api_call(logger, "GET", url)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get("results", [])
    
    async def get_clash_test_resources(self, clash_test_id: str) -> Dict[str, Any]:
        """
        Get clash test resources/details.
        
        GET https://developer.api.autodesk.com/bim360/clash/v3/containers/:containerId/tests/:testId/resources
        """
        url = (
            f"{self.base_url}/bim360/clash/v3/"
            f"containers/{self.project_id}/tests/{clash_test_id}/resources"
        )
        
        headers = await self._get_headers()
        log_api_call(logger, "GET", url)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
    
    async def get_assigned_clash_groups(
        self,
        test_id: str,
        offset: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get assigned clash groups for a clash test.
        
        GET https://developer.api.autodesk.com/bim360/clash/v3/containers/:containerId/tests/:testId/clashes/assigned
        """
        url = (
            f"{self.base_url}/bim360/clash/v3/"
            f"containers/{self.project_id}/tests/{test_id}/clashes/assigned"
        )
        
        params = {"offset": offset, "limit": limit}
        headers = await self._get_headers()
        log_api_call(logger, "GET", url, params=params)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get("pagination", {}).get("results", [])
    
    def _normalize_clash(self, raw: Dict[str, Any]) -> Clash:
        """
        Normalize raw APS clash data to internal Clash model.
        
        Adjust field mapping based on actual API response structure.
        """
        # Extract basic info
        clash_id = raw.get("id", "unknown")
        group_id = raw.get("groupId", "default")
        title = raw.get("name", "Unnamed Clash")
        
        # Map status
        status_str = raw.get("status", "open").lower()
        status = ClashStatus(status_str) if status_str in ["open", "resolved", "suppressed"] else ClashStatus.OPEN
        
        # Map severity (if not provided, infer from distance or default to medium)
        severity_str = raw.get("severity", "medium").lower()
        severity = ClashSeverity(severity_str) if severity_str in ["high", "medium", "low"] else ClashSeverity.MEDIUM
        
        # Elements
        element_a_data = raw.get("elementA", {})
        element_b_data = raw.get("elementB", {})
        
        element_a = Element(
            urn=element_a_data.get("urn", ""),
            guid=element_a_data.get("guid", ""),
            name=element_a_data.get("name", ""),
            category=element_a_data.get("category", "")
        )
        
        element_b = Element(
            urn=element_b_data.get("urn", ""),
            guid=element_b_data.get("guid", ""),
            name=element_b_data.get("name", ""),
            category=element_b_data.get("category", "")
        )
        
        # Location
        location_data = raw.get("location", {})
        location = Location(
            x=location_data.get("x", 0.0),
            y=location_data.get("y", 0.0),
            z=location_data.get("z", 0.0),
            level=location_data.get("level")
        )
        
        # Disciplines
        discipline_a = element_a_data.get("discipline", "")
        discipline_b = element_b_data.get("discipline", "")
        
        # Links
        acc_link = raw.get("accLink") or f"https://acc.autodesk.com/projects/{self.project_id}/clashes/{clash_id}"
        
        return Clash(
            id=clash_id,
            group_id=group_id,
            title=title,
            status=status,
            severity=severity,
            discipline_a=discipline_a,
            discipline_b=discipline_b,
            element_a=element_a,
            element_b=element_b,
            location=location,
            screenshot_url=None,
            acc_link=acc_link,
            created_at=raw.get("createdAt"),
            updated_at=raw.get("updatedAt")
        )
    
    async def fetch_all_clashes(self) -> List[Clash]:
        """
        Fetch all clashes from the model set.
        
        This iterates through clash tests and aggregates assigned clash groups.
        """
        logger.info("Fetching clashes from APS Model Coordination")
        logger.info(f"Configured Model Set ID: {self.modelset_id}")
        logger.info(f"Container (Project) ID: {self.project_id}")
        
        all_clashes: List[Clash] = []
        
        try:
            # First, list all available model sets to verify the configured one exists
            logger.info("Listing available model sets...")
            model_sets = await self.list_model_sets()
            logger.info(f"Found {len(model_sets)} model sets in project")
            
            if model_sets:
                for ms in model_sets:
                    logger.info(f"  - Model Set: {ms.get('name')} (ID: {ms.get('id')})")
            
            # Check if our configured model set exists
            model_set_exists = any(ms.get('id') == self.modelset_id for ms in model_sets)
            
            if not model_set_exists and model_sets:
                logger.warning(f"Configured model set {self.modelset_id} not found!")
                logger.warning(f"Using first available model set instead")
                self.modelset_id = model_sets[0].get('id')
                logger.info(f"Using model set: {model_sets[0].get('name')} ({self.modelset_id})")
            
            # Get clash tests for the model set
            clash_tests = await self.list_clash_tests()
            logger.info(f"Found {len(clash_tests)} clash tests in model set")
            
            # Fetch assigned clash groups for each test
            for test in clash_tests:
                test_id = test.get("id")
                if not test_id:
                    continue
                
                logger.info(f"Fetching clashes for test {test_id}")
                
                # Paginate through clash groups
                offset = 0
                limit = 100
                
                while True:
                    clash_groups = await self.get_assigned_clash_groups(test_id, offset, limit)
                    if not clash_groups:
                        break
                    
                    logger.debug(f"Retrieved {len(clash_groups)} clash groups (offset={offset})")
                    
                    # Normalize and add clashes
                    for raw_clash in clash_groups:
                        try:
                            clash = self._normalize_clash(raw_clash)
                            all_clashes.append(clash)
                        except Exception as e:
                            logger.error(f"Failed to normalize clash: {e}", exc_info=True)
                    
                    # Check if more pages
                    if len(clash_groups) < limit:
                        break
                    
                    offset += limit
            
            logger.info(f"Successfully fetched {len(all_clashes)} clashes from APS")
            return all_clashes
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching clashes: {e}")
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching clashes: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching clashes: {e}", exc_info=True)
            raise


def get_mc_client() -> APSMCClient:
    """Get Model Coordination client instance."""
    return APSMCClient()
