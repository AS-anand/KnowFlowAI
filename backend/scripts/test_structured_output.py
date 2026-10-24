
import asyncio
from dotenv import load_dotenv

from app.models.summary_models import DocumentSummary
from app.services.llm.groq_provider import GroqProvider


async def main():
    load_dotenv()

    provider = GroqProvider()

    document = """
    Employee Leave Policy

    The company provides 20 paid leaves annually to eligible
    employees. Employees can request leave through the HR portal.

    Unused leaves can be carried forward up to a maximum of
    5 days. Leave requests must be approved by the reporting manager.
    """

    system_prompt = """
    You are a document analysis assistant.

    Analyse the provided document and return:
    - A concise summary
    - Important key points
    - Document category
    - Important entities

    Use only information from the document.
    Do not invent information.
    """

    user_prompt = f"""
    Analyse this document:

    <document>
    {document}
    </document>
    """

    try:
        result = await provider.generate_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=DocumentSummary
        )

        print("\nSTRUCTURED OUTPUT:")
        print(result.model_dump_json(indent=2))

        print("\nPYTHON OBJECT:")
        print(type(result))

        print("\nKEY POINTS:")
        for point in result.key_points:
            print("-", point)

    finally:
        await provider.close()


if __name__ == "__main__":
    asyncio.run(main())
