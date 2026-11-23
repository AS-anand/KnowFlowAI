
import asyncio

from uuid import UUID

from app.services.embedding_service import EmbeddingService
from app.services.vector_search_service import VectorSearchService


DOCUMENT_ID = UUID(
    "b5bfba19-4f11-48e5-be3e-aa5619136c96"
)

QUERIES = [
    "What are the four laws of behavior change?",
    "What is James Clear's current residential address?",
    (
        "What are the four laws of behavior change, "
        "and what is James Clear's current residential address?"
    ),
]


def main():
    embedding_service = EmbeddingService()
    vector_search_service = VectorSearchService()

    for question in QUERIES:
        print("\n" + "=" * 80)
        print(f"QUESTION: {question}")
        print("=" * 80)

        query_embedding = embedding_service.embed_query(question)

        

        results = vector_search_service.search(
            query_embedding,
            [DOCUMENT_ID],
            20,
            None,
            None,
            None,
        )

        print(f"Retrieved chunks: {len(results)}")

        for rank, chunk in enumerate(results, start=1):
            print(
                f"\nRank: {rank}"
                f"\nPage: {chunk['page_number']}"
                f"\nSimilarity: {chunk['similarity']}"
                f"\nContent: {chunk['content'][:300]}"
            )


if __name__ == "__main__":
    main()
