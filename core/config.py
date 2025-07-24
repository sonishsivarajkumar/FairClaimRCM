"""
Configuration settings for FairClaimRCM

Handles environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "FairClaimRCM"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/fairclaimrcm"
    
    # Elasticsearch settings
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX_PREFIX: str = "fairclaimrcm"
    
    # ML/AI settings
    MODEL_CACHE_DIR: str = "./models"
    DEFAULT_CONFIDENCE_THRESHOLD: float = 0.7
    
    # Healthcare data settings
    ICD10_DATA_PATH: str = "./data/terminology/icd10.json"
    CPT_DATA_PATH: str = "./data/terminology/cpt.json"
    DRG_DATA_PATH: str = "./data/terminology/drg.json"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
