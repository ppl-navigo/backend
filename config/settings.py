from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

class Settings:
    """Configuration settings for API keys and services."""
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

settings = Settings()