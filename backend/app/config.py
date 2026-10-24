import os
from pathlib import Path
from dotenv import load_dotenv

# Locate backend/.env explicitly
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)


class Settings:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-20b"
        )

        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is not configured")


settings = Settings()