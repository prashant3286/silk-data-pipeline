import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

class Settings:
    """
    Application configuration settings
    """
    QUALYS_API_TOKEN = os.environ.get("QUALYS_API_TOKEN")
    CROWDSTRIKE_API_TOKEN = os.environ.get("CROWDSTRIKE_API_TOKEN")
    BASE_URL = os.environ.get("BASE_URL")
    MONGODB_URI= os.environ.get("MONGODB_URI")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")
    API_REQUEST_TIMEOUT= int(os.environ.get("API_REQUEST_TIMEOUT"))
    PAGINATION_LIMIT= int(os.environ.get("PAGINATION_LIMIT"))

# Create a singleton settings instance
settings = Settings()