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
        self.database_url = os.getenv("DATABASE_URL")
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        

        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is not configured")

        if not self.database_url:
            raise ValueError("DATABASE_URL is not configured")

        if not self.jwt_secret_key:
            raise ValueError("JWT_SECRET_KEY is not configured")


settings = Settings()