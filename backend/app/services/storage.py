"""File storage service for captures and exports."""
import base64
import os
from pathlib import Path
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class StorageService:
    """Service for managing file storage."""
    
    def __init__(self):
        self.exports_dir = Path(settings.exports_dir)
        self.captures_dir = Path(settings.captures_dir)
        
        # Ensure directories exist
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.captures_dir.mkdir(parents=True, exist_ok=True)
    
    def save_capture(self, clash_id: str, image_data_url: str) -> str:
        """
        Save a base64-encoded image capture.
        
        Args:
            clash_id: Clash identifier
            image_data_url: Data URL with base64 image (data:image/png;base64,...)
            
        Returns:
            Path to saved file
        """
        try:
            # Parse data URL
            if "base64," in image_data_url:
                image_data = image_data_url.split("base64,")[1]
            else:
                image_data = image_data_url
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            
            # Save to file
            filename = f"{clash_id}.png"
            filepath = self.captures_dir / filename
            
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            
            logger.info(f"Saved capture for clash {clash_id}: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save capture for clash {clash_id}: {e}")
            raise
    
    def get_capture_path(self, clash_id: str) -> Optional[Path]:
        """Get path to capture if it exists."""
        filepath = self.captures_dir / f"{clash_id}.png"
        return filepath if filepath.exists() else None
    
    def save_report(self, filename: str, pdf_bytes: bytes) -> str:
        """
        Save a PDF report.
        
        Args:
            filename: Report filename
            pdf_bytes: PDF binary data
            
        Returns:
            Path to saved file
        """
        filepath = self.exports_dir / filename
        
        with open(filepath, "wb") as f:
            f.write(pdf_bytes)
        
        logger.info(f"Saved report: {filepath}")
        return str(filepath)
    
    def get_latest_report(self) -> Optional[Path]:
        """Get path to the most recent report."""
        reports = sorted(
            self.exports_dir.glob("*.pdf"),
            key=os.path.getmtime,
            reverse=True
        )
        return reports[0] if reports else None


# Global storage service
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get or create the global storage service."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
