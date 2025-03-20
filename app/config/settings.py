from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

class Settings:
    """Configuration settings for API keys and AI prompts."""
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    AI_RISK_ANALYSIS_PROMPT = os.getenv("AI_RISK_ANALYSIS_PROMPT")
    SITE_URL = os.getenv("SITE_URL", "https://yourwebsite.com")  # Optional ranking
    SITE_NAME = os.getenv("SITE_NAME", "YourApp")  # Optional ranking
    AI_OUTPUT = os.getenv("AI_OUTPUT") # temporary aja sampe API self deployment done
    OLLAMA_URL = os.getenv("OLLAMA_URL")

settings = Settings()