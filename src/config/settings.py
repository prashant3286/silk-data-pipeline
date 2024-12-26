import os
class Settings:
    """
    Application configuration settings
    """
    QUALYS_API_TOKEN = os.environ.get("QUALYS_API_TOKEN")
    CROWDSTRIKE_API_TOKEN = os.environ.get("CROWDSTRIKE_API_TOKEN")
    
    
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "host_pipeline"
    
    API_REQUEST_TIMEOUT: int = 30
    PAGINATION_LIMIT: int = 2
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a singleton settings instance
settings = Settings()