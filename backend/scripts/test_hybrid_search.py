
from uuid import UUID

from app.services.embedding_service import EmbeddingService
from app.services.keyword_search_service import KeywordSearchService
from app.services.vector_search_service import VectorSearchService
from app.services.hybrid_search_service import HybridSearchService


embedding_service = EmbeddingService()
keyword_service = KeywordSearchService()
vector_service = VectorSearchService()

hybrid_service = HybridSearchService(
    embedding_service=embedding_service,
    keyword_search_service=keyword_service,
    vector_search_service=vector_service,
)

document_ids = [
    UUID("b5bfba19-4f11-48e5-be3e-aa5619136c96")
]

test_questions = [
    # Test 1: Exact terminology
    "four laws of behavior change",

    # Test 2: Semantic paraphrase
    "How can I make good habits easier to follow?",

    # Test 3: Combined conceptual question
    "What are the four laws and how do they help build habits?",
]


def print_results(title, results):
    print(f"\n--- {title} ---")

    if not results:
        print("No results found.")
        return

    for rank, result in enumerate(results, start=1):
        print({
            "rank": rank,
            "chunk_id": result["id"],
            "page": result["page_number"],
            "score": round(
                result.get(
                    "rrf_score",
                    result.get(
                        "similarity",
                        result.get("rank_score", 0)
                    )
                ),
                6,
            ),
            "keyword_rank": result.get("keyword_rank"),
            "semantic_rank": result.get("semantic_rank"),
            "retrieval_methods": result.get("retrieval_methods"),
        })


for question in test_questions:

    print("\n" + "=" * 80)
    print(f"QUESTION: {question}")
    print("=" * 80)

    keyword_results = keyword_service.search(
        query=question,
        document_ids=document_ids,
        top_k=5,
    )

    query_embedding = embedding_service.embed_query(question)

    semantic_results = vector_service.search(
        query_embedding=query_embedding,
        document_ids=document_ids,
        top_k=5,
    )

    hybrid_results = hybrid_service.search(
        query=question,
        document_ids=document_ids,
        top_k=5,
    )

    print_results("KEYWORD SEARCH", keyword_results)
    print_results("SEMANTIC SEARCH", semantic_results)
    print_results("HYBRID SEARCH", hybrid_results)
