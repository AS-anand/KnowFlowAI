
import asyncio
from dotenv import load_dotenv

from app.services.llm.groq_provider import GroqProvider


async def main():
    load_dotenv()

    provider = GroqProvider()

    prompt = """
    Write a short, creative description of a rainy evening
    in a city. Use approximately 50 words.
    """

    top_p_values = [0.3, 0.7, 1.0]

    try:
        for top_p in top_p_values:

            result = await provider.generate(
                system_prompt="You are a creative writer.",
                user_prompt=prompt,
                temperature=0.7,
                top_p=top_p
            )

            print("\n" + "=" * 50)
            print(f"TOP-P: {top_p}")
            print("=" * 50)
            print(result)

    finally:
        await provider.close()


if __name__ == "__main__":
    asyncio.run(main())
