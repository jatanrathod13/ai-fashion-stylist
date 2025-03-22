"""
Configuration module for the AI Fashion Stylist Assistant

This module manages environment variables and provides configuration settings
for various components of the application.
"""
import os
from pydantic import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API settings
    API_VERSION: str = "v1"
    APP_NAME: str = "AI Fashion Stylist Assistant"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_VISION_MODEL: str = os.getenv("OPENAI_VISION_MODEL", "gpt-4o")
    OPENAI_TEXT_MODEL: str = os.getenv("OPENAI_TEXT_MODEL", "gpt-4o")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
    
    # Weaviate settings
    WEAVIATE_URL: str = os.getenv("WEAVIATE_URL", "")
    WEAVIATE_API_KEY: str = os.getenv("WEAVIATE_API_KEY", "")
    
    # File storage
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")  # local, s3, etc.
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
    
    # Firecrawl settings (for e-commerce crawling)
    FIRECRAWL_API_KEY: str = os.getenv("FIRECRAWL_API_KEY", "")
    
    # Perplexity settings (for research)
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fashion_stylist.db")
    
    class Config:
        """Pydantic config"""
        case_sensitive = True
        env_file = ".env"


# Create settings instance
settings = Settings()

# Validate essential settings
def validate_settings():
    """Validate that required settings are configured"""
    if not settings.SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set")
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable must be set")
    # In production, you'd want to validate these too
    # if not settings.WEAVIATE_URL or not settings.WEAVIATE_API_KEY:
    #     raise ValueError("Weaviate configuration is incomplete")


# Validate settings on import (in production)
if not settings.DEBUG:
    validate_settings() 