
from uuid import UUID

from app.services.embedding_service import EmbeddingService
from app.services.vector_search_service import VectorSearchService
from app.services.reranking.reranker_service import RerankerService


# Configuration
document_ids = [
    UUID("b5bfba19-4f11-48e5-be3e-aa5619136c96")
]

question = "What are the four laws and how do they help build habits?"

final_top_k = 5
candidate_k = 20


# Initialize services.
embedding_service = EmbeddingService()
vector_service = VectorSearchService()
reranker_service = RerankerService()


# Generate query embedding once.
query_embedding = embedding_service.embed_query(question)


# Stage 1: Retrieve semantic candidates.
candidate_documents = vector_service.search(
    query_embedding=query_embedding,
    document_ids=document_ids,
    top_k=candidate_k,
    similarity_threshold=None,
)


print("\n========== BASELINE: SEMANTIC RETRIEVAL ==========")

baseline_documents = candidate_documents[:final_top_k]

for rank, document in enumerate(baseline_documents, start=1):
    print({
        "rank": rank,
        "chunk_id": document["id"],
        "page": document["page_number"],
        "similarity": round(document["similarity"], 4),
        "content": document["content"][:300],
    })


# Stage 2: Rerank the same candidate pool.
reranked_documents = reranker_service.rerank(
    query=question,
    documents=candidate_documents,
    top_k=final_top_k,
)


print("\n========== AFTER CROSS-ENCODER RERANKING ==========")

for document in reranked_documents:
    print({
        "rank": document["rerank_rank"],
        "chunk_id": document["id"],
        "page": document["page_number"],
        "similarity": round(document["similarity"], 4),
        "rerank_score": round(document["rerank_score"], 4),
        "content": document["content"][:300],
    })


# Stage 3: Compare chunk movement.
baseline_ids = {
    document["id"]: rank
    for rank, document in enumerate(baseline_documents, start=1)
}

print("\n========== RANKING COMPARISON ==========")

for document in reranked_documents:
    chunk_id = document["id"]
    baseline_rank = baseline_ids.get(chunk_id)

    print({
        "chunk_id": chunk_id,
        "baseline_rank": baseline_rank,
        "reranked_rank": document["rerank_rank"],
        "movement": (
            "Newly promoted into top 5"
            if baseline_rank is None
            else (
                f"Moved up {baseline_rank - document['rerank_rank']} positions"
                if baseline_rank > document["rerank_rank"]
                else (
                    f"Moved down {document['rerank_rank'] - baseline_rank} positions"
                    if baseline_rank < document["rerank_rank"]
                    else "No change"
                )
            )
        ),
    })
