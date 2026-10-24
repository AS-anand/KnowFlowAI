import os
from unittest.mock import patch

from app.config import Settings

with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
    try:
        Settings()
        print("Test failed: missing API key was accepted")
    except ValueError as exc:
        print(f"Test passed: {exc}")