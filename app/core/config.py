import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database configuration
    DATABASE_URL: str = "sqlite:///./data/pim.db"
    
    # Supabase configuration
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"  # JWT algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # JWT token expiration
    
    # AI Service configuration
    OPENAI_API_KEY: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings() 