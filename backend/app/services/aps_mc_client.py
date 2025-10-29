"""Autodesk Platform Services Model Coordination client.

Implements the official APS Model Coordination API workflow for retrieving clash data.
Based on: https://aps.autodesk.com/en/docs/acc/v1/tutorials/model-coordination/mc-tutorial-clash/

The workflow is:
1. Get the latest model set version
2. Get clash tests for that version
3. Get resource URLs for test results
4. Download and decompress JSON.gz files
5. Parse and map clash data
"""
import gzip
import json
from io import BytesIO
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings
from app.core.logging import get_logger, log_api_call
from app.models.clash import Clash, ClashSeverity, ClashStatus, Element, Location
from app.services.aps_auth import get_auth_client

logger = get_logger(__name__)


class APSMCClient:
    """Client for APS Model Coordination API following official tutorial workflow."""
    
    def __init__(self):
        self.base_url = settings.aps_base_url
        self.project_id = settings.aps_project_id
        self.modelset_id = settings.aps_modelset_id
        self.auth_client = get_auth_client()
    
    async def _get_headers(self) -> Dict[str, str]:
        """Get headers with auth token."""
        token = await self.auth_client.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    async def get_latest_model_set_version(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest version of the model set.
        
        GET /bim360/modelset/v3/containers/:containerId/modelsets/:modelSetId/versions/latest
        """
        url = (
            f"{self.base_url}/bim360/modelset/v3/"
            f"containers/{self.project_id}/modelsets/{self.modelset_id}/versions/latest"
        )
        
        headers = await self._get_headers()
        log_api_call(logger, "GET", url)
        
        async with httpx.AsyncClient(timeout=100.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    
    async def get_clash_tests_for_version(self, version: int) -> List[Dict[str, Any]]:
        """
        Get clash tests for a specific model set version.
        
        GET /bim360/clash/v3/containers/:containerId/modelsets/:modelSetId/versions/:version/tests
        """
        url = (
            f"{self.base_url}/bim360/clash/v3/"
            f"containers/{self.project_id}/modelsets/{self.modelset_id}/versions/{version}/tests"
        )
        
        headers = await self._get_headers()
        log_api_call(logger, "GET", url)
        
        async with httpx.AsyncClient(timeout=100.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get("tests", [])
    
    async def get_test_resources(self, test_id: str) -> List[Dict[str, Any]]:
        """
        Get downloadable resource URLs for a clash test.
        
        GET /bim360/clash/v3/containers/:containerId/tests/:testId/resources
        
        Returns URLs to download:
        - scope-version-clash.*.*.*.json.gz: Pairwise clash results
        - scope-version-clash-instance.*.*.*.json.gz: Viewable data for clashed objects
        - scope-version-document.*.*.*.json.gz: Document URNs for objects
        """
        url = (
            f"{self.base_url}/bim360/clash/v3/"
            f"containers/{self.project_id}/tests/{test_id}/resources"
        )
        
        headers = await self._get_headers()
        log_api_call(logger, "GET", url)
        
        async with httpx.AsyncClient(timeout=100.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return data.get("resources", [])
    
    async def download_and_decompress_resource(self, url: str) -> Dict[str, Any]:
        """
        Download a JSON resource and decompress it if needed.
        
        The resource may be gzip-compressed or plain JSON (sometimes with UTF-8 BOM).
        
        Args:
            url: The direct download URL from get_test_resources
            
        Returns:
            The JSON data as a dictionary
        """
        log_api_call(logger, "GET", url)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            data = response.content
            
            # Check if data is gzip-compressed (starts with magic number 1f 8b)
            if len(data) >= 2 and data[0] == 0x1f and data[1] == 0x8b:
                logger.debug("Resource is gzip-compressed, decompressing...")
                try:
                    with gzip.GzipFile(fileobj=BytesIO(data)) as gz:
                        json_data = gz.read().decode('utf-8')
                except Exception as e:
                    logger.error(f"Failed to decompress gzip data: {e}")
                    raise
            else:
                # Plain JSON (possibly with UTF-8 BOM)
                logger.debug("Resource is plain JSON")
                json_data = data.decode('utf-8')
                
                # Remove UTF-8 BOM if present (ef bb bf)
                if json_data.startswith('\ufeff'):
                    json_data = json_data[1:]
            
            return json.loads(json_data)
    
    def _map_clash_data(
        self,
        clash_data: Dict[str, Any],
        instance_data: Dict[str, Any],
        document_data: Dict[str, Any]
    ) -> List[Clash]:
        """
        Map the three resource files together to create Clash objects.
        
        Following the official tutorial mapping:
        - clash_data: Contains clash IDs and stable object IDs
        - instance_data: Maps clash IDs to viewable IDs
        - document_data: Maps document IDs to URNs
        
        Args:
            clash_data: Data from scope-version-clash.*.*.*.json.gz
            instance_data: Data from scope-version-clash-instance.*.*.*.json.gz
            document_data: Data from scope-version-document.*.*.*.json.gz
            
        Returns:
            List of Clash objects
        """
        clashes: List[Clash] = []
        
        # Build document lookup: doc_id -> document info
        documents = {}
        for doc in document_data.get("documents", []):
            doc_id = doc.get("id")
            if doc_id is not None:
                documents[doc_id] = doc
        
        # Build instance lookup: clash_id -> instance info
        instances = {}
        for instance in instance_data.get("instances", []):
            cid = instance.get("cid")  # clash ID
            if cid is not None:
                if cid not in instances:
                    instances[cid] = []
                instances[cid].append(instance)
        
        # Process each clash
        for clash in clash_data.get("clashes", []):
            try:
                clash_id = clash.get("id")
                if clash_id is None:
                    continue
                
                # Get instance data for this clash
                clash_instances = instances.get(clash_id, [])
                if len(clash_instances) < 2:
                    logger.warning(f"Clash {clash_id} has fewer than 2 instances, skipping")
                    continue
                
                # Typically there are 2 instances (left and right object)
                left_instance = clash_instances[0]
                right_instance = clash_instances[1] if len(clash_instances) > 1 else clash_instances[0]
                
                # Get document info
                left_doc_id = left_instance.get("ldid")
                right_doc_id = right_instance.get("rdid")
                
                left_doc = documents.get(left_doc_id, {})
                right_doc = documents.get(right_doc_id, {})
                
                # Extract element information
                element_a = Element(
                    urn=left_doc.get("urn", ""),
                    guid=str(left_instance.get("loid", "")),  # stable object ID
                    name=left_instance.get("name", f"Object {left_instance.get('lvid', '')}"),
                    category=left_instance.get("category", "")
                )
                
                element_b = Element(
                    urn=right_doc.get("urn", ""),
                    guid=str(right_instance.get("roid", "")),  # stable object ID
                    name=right_instance.get("name", f"Object {right_instance.get('rvid', '')}"),
                    category=right_instance.get("category", "")
                )
                
                # Extract location if available
                location_data = clash.get("location", {})
                location = Location(
                    x=location_data.get("x", 0.0),
                    y=location_data.get("y", 0.0),
                    z=location_data.get("z", 0.0),
                    level=location_data.get("level")
                )
                
                # Determine severity based on distance or type
                distance = clash.get("distance", 0)
                if distance < 0.01:  # < 1cm
                    severity = ClashSeverity.HIGH
                elif distance < 0.05:  # < 5cm
                    severity = ClashSeverity.MEDIUM
                else:
                    severity = ClashSeverity.LOW
                
                # Status - clashes from files are typically active
                status = ClashStatus.OPEN
                
                # Build clash object parameters (don't pass None for timestamps)
                clash_params = {
                    "id": str(clash_id),
                    "group_id": clash.get("groupId", "default"),
                    "title": f"Clash {clash_id}",
                    "status": status,
                    "severity": severity,
                    "discipline_a": left_doc.get("discipline", ""),
                    "discipline_b": right_doc.get("discipline", ""),
                    "element_a": element_a,
                    "element_b": element_b,
                    "location": location,
                    "screenshot_url": None,
                    "acc_link": f"https://acc.autodesk.com/projects/{self.project_id}/clashes/{clash_id}",
                }
                
                # Only add timestamps if they exist (otherwise Pydantic will use default_factory)
                created_at = clash.get("createdAt")
                if created_at:
                    clash_params["created_at"] = created_at
                
                updated_at = clash.get("updatedAt")
                if updated_at:
                    clash_params["updated_at"] = updated_at
                
                # Create clash object
                clash_obj = Clash(**clash_params)
                
                clashes.append(clash_obj)
                
            except Exception as e:
                logger.error(f"Failed to map clash {clash.get('id')}: {e}", exc_info=True)
                continue
        
        return clashes
    
    async def fetch_all_clashes(self) -> List[Clash]:
        """
        Fetch all clashes following the official APS tutorial workflow.
        
        Workflow:
        1. Get latest model set version
        2. Get clash tests for that version
        3. For each test, get resource URLs
        4. Download and decompress the 3 key resource files
        5. Map the data together to create Clash objects
        """
        logger.info("Fetching clashes from APS Model Coordination (Official Workflow)")
        logger.info(f"Model Set ID: {self.modelset_id}")
        logger.info(f"Container (Project) ID: {self.project_id}")
        
        all_clashes: List[Clash] = []
        
        try:
            # Step 1: Get latest model set version
            logger.info("Step 1: Getting latest model set version...")
            version_data = await self.get_latest_model_set_version()
            version_num = version_data.get("version")
            version_status = version_data.get("status")
            
            logger.info(f"Latest version: {version_num}, Status: {version_status}")
            
            if version_status != "Successful":
                logger.warning(f"Model set version {version_num} status is not 'Successful': {version_status}")
                return []
            
            # Step 2: Get clash tests for this version
            logger.info(f"Step 2: Getting clash tests for version {version_num}...")
            clash_tests = await self.get_clash_tests_for_version(version_num)
            
            logger.info(f"Found {len(clash_tests)} clash tests")
            
            if not clash_tests:
                logger.warning("No clash tests found for this model set version")
                logger.info("Note: Clash tests must be created and run in ACC Model Coordination")
                return []
            
            # Step 3-5: Process each clash test
            for test in clash_tests:
                test_id = test.get("id")
                test_status = test.get("status")
                
                logger.info(f"Processing clash test {test_id} (Status: {test_status})")
                
                if test_status != "Success":
                    logger.warning(f"Test {test_id} status is not 'Success': {test_status}, skipping")
                    continue
                
                try:
                    # Step 3: Get resource URLs
                    logger.info(f"Step 3: Getting resource URLs for test {test_id}...")
                    resources = await self.get_test_resources(test_id)
                    
                    logger.info(f"Found {len(resources)} resources")
                    
                    # Find the 3 key resource files
                    clash_resource = None
                    instance_resource = None
                    document_resource = None
                    
                    for resource in resources:
                        resource_type = resource.get("type", "")
                        if "scope-version-clash." in resource_type and "instance" not in resource_type:
                            clash_resource = resource
                        elif "scope-version-clash-instance." in resource_type:
                            instance_resource = resource
                        elif "scope-version-document." in resource_type:
                            document_resource = resource
                    
                    if not all([clash_resource, instance_resource, document_resource]):
                        logger.warning(f"Missing required resources for test {test_id}")
                        logger.debug(f"clash: {bool(clash_resource)}, instance: {bool(instance_resource)}, document: {bool(document_resource)}")
                        continue
                    
                    # Step 4: Download and decompress each resource
                    logger.info("Step 4: Downloading and decompressing resources...")
                    
                    logger.info("Downloading clash data...")
                    clash_data = await self.download_and_decompress_resource(clash_resource["url"])
                    
                    logger.info("Downloading instance data...")
                    instance_data = await self.download_and_decompress_resource(instance_resource["url"])
                    
                    logger.info("Downloading document data...")
                    document_data = await self.download_and_decompress_resource(document_resource["url"])
                    
                    # Step 5: Map data together
                    logger.info("Step 5: Mapping clash data...")
                    test_clashes = self._map_clash_data(clash_data, instance_data, document_data)
                    
                    logger.info(f"Mapped {len(test_clashes)} clashes from test {test_id}")
                    all_clashes.extend(test_clashes)
                    
                except Exception as e:
                    logger.error(f"Error processing test {test_id}: {e}", exc_info=True)
                    continue
            
            logger.info(f"✅ Successfully fetched {len(all_clashes)} clashes from APS")
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
