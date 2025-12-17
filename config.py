from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    
    Note: Since Rise CRM API doesn't have endpoints to list lead statuses
    and sources, we use hardcoded IDs that need to be configured manually.
    """
    
    # Rise CRM API
    rise_base_url: str
    rise_api_token: str
    
    # Default owner email for fallback
    default_owner_email: str
    
    # Lead Status and Source IDs (must be configured based on Rise CRM setup)
    # These IDs need to be obtained from the Rise CRM admin panel
    default_lead_status_id: int = 1  # "Novo Lead" status ID
    default_lead_source_id: int = 1  # "Kixie" source ID
    
    # Optional: Default owner ID (if known)
    default_owner_id: int = 1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra env vars


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
