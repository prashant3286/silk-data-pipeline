from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application configuration settings
    """
    QUALYS_API_TOKEN: str = "armis-login@armis.com_60974105-5053-4267-b16e-392e8165c89a"
    CROWDSTRIKE_API_TOKEN: str = "armis-login@armis.com_60974105-5053-4267-b16e-392e8165c89a"
    
    
    MONGODB_URI: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "host_pipeline"
    
    API_REQUEST_TIMEOUT: int = 30
    PAGINATION_LIMIT: int = 100
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a singleton settings instance
settings = Settings()