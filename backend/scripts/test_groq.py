import asyncio
from dotenv import load_dotenv

from app.services.llm.groq_provider import GroqProvider


async def main():
    load_dotenv()

    provider = GroqProvider()

    try:
        answer = await provider.generate(
            system_prompt=(
                "You are a helpful AI assistant. "
                "Answer clearly and concisely."
            ),
            user_prompt="Explain what RAG means in AI."
        )

        print("\nGroq response:")
        print(answer)

    finally:
        await provider.close()


if __name__ == "__main__":
    asyncio.run(main())