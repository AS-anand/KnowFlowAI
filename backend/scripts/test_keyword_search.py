
from uuid import UUID

from app.services.keyword_search_service import KeywordSearchService
from app.services.embedding_service import EmbeddingService
from app.services.vector_search_service import VectorSearchService


# Initialize services
keyword_service = KeywordSearchService()
embedding_service = EmbeddingService()
vector_service = VectorSearchService()

document_ids = [
    UUID("b5bfba19-4f11-48e5-be3e-aa5619136c96")
]

TOP_K = 5

questions = [
    "four laws of behavior change",
    "How can I make good habits easier to follow?",
    "What are the four laws and how do they help build habits?",
]


def print_results(search_type, results, score_key):

    print(f"\n{'=' * 80}")
    print(f"{search_type} SEARCH")
    print(f"{'=' * 80}")

    if not results:
        print("No results found.")
        return

    for rank, result in enumerate(results, start=1):
        print(f"\nRank: {rank}")
        print(f"Chunk ID: {result['id']}")
        print(f"File: {result['file_name']}")
        print(f"Page: {result['page_number']}")
        print(f"Chunk index: {result['chunk_index']}")
        print(f"Score: {result[score_key]:.6f}")
        print(f"Content:\n{result['content']}")


for question in questions:

    print("\n\n" + "#" * 100)
    print(f"QUESTION: {question}")
    print("#" * 100)

    # 1. Keyword search
    keyword_results = keyword_service.search(
        query=question,
        document_ids=document_ids,
        top_k=TOP_K,
    )

    # 2. Generate query embedding
    query_embedding = embedding_service.embed_query(question)

    # 3. Semantic search
    semantic_results = vector_service.search(
        query_embedding=query_embedding,
        document_ids=document_ids,
        top_k=TOP_K,
        similarity_threshold=None,
    )

    # 4. Display results
    print_results(
        "KEYWORD",
        keyword_results,
        "rank_score",
    )

    print_results(
        "SEMANTIC",
        semantic_results,
        "similarity",
    )
