"""Configuration management with environment variables."""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Autodesk Platform Services
    aps_client_id: Optional[str] = None
    aps_client_secret: Optional[str] = None
    aps_account_id: Optional[str] = None
    aps_project_id: Optional[str] = None
    aps_coordination_space_id: Optional[str] = None
    aps_modelset_id: Optional[str] = None
    
    # Application
    use_mock: bool = True
    log_level: str = "INFO"
    api_port: int = 8000
    frontend_port: int = 8501
    
    # CORS
    cors_origins: str = "http://localhost:8501,http://localhost:3000"
    
    # Storage
    exports_dir: str = "exports"
    captures_dir: str = "captures"
    
    # APS URLs
    aps_auth_url: str = "https://developer.api.autodesk.com/authentication/v2/token"
    aps_base_url: str = "https://developer.api.autodesk.com"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def has_aps_credentials(self) -> bool:
        """Check if APS credentials are configured."""
        return bool(
            self.aps_client_id 
            and self.aps_client_secret
            and self.aps_account_id
            and self.aps_project_id
        )
    
    @property
    def is_mock_mode(self) -> bool:
        """Determine if app should run in mock mode."""
        return self.use_mock or not self.has_aps_credentials
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
