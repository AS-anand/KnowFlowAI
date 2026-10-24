
import os

from groq import AsyncGroq
from pydantic import BaseModel
from groq import AsyncGroq
from app.config import settings


class GroqProvider:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is not configured")

        self.model = settings.groq_model

        self.client = AsyncGroq(
            api_key=settings.groq_api_key,
            timeout=30.0,
            max_retries=2
        )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        top_p: float = 1.0
    ) -> str:

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            top_p=top_p
        )

        return response.choices[0].message.content or ""

    async def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel]
    ) -> BaseModel:

        schema = response_model.model_json_schema()

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "document_summary",
                    "strict": True,
                    "schema": schema
                }
            }
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("Groq returned an empty response")

        return response_model.model_validate_json(content)

    async def close(self):
        await self.client.close()
