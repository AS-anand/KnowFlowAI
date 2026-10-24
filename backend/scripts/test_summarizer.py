
import asyncio
from dotenv import load_dotenv

from app.services.llm.groq_provider import GroqProvider
from app.services.document_summarizer import DocumentSummarizer

from groq import (
    AuthenticationError,
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    APIStatusError
)


async def main():
    load_dotenv()

    provider = GroqProvider()
    summarizer = DocumentSummarizer(provider)

    document_text = """
    Employee Leave Policy

    The company provides 20 paid leaves annually to eligible
    employees. Employees can request leave through the HR portal.

    Unused leaves can be carried forward up to a maximum of
    5 days. Leave requests must be approved by the reporting manager.
    """

    try:
        result = await summarizer.summarize(document_text)
        print(result.model_dump_json(indent=2))
        
    except AuthenticationError:
        print("Invalid Groq API key. Check your configuration.")
        
    except RateLimitError:
        print("Groq rate limit reached. Try again later.")

    except APITimeoutError:
        print("Groq request timed out.")

    except APIConnectionError:
        print("Could not connect to Groq.")

    except APIStatusError as exc:
        print(f"Groq API error: {exc.status_code}")

    except ValueError as exc:
        print(f"Invalid input: {exc}")

    finally:
        await provider.close()


if __name__ == "__main__":
    asyncio.run(main())
