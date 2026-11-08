
from statistics import median
from time import perf_counter
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
candidate_sizes = [5, 10, 20, 30]
num_trials = 3


# Initialize services.
embedding_service = EmbeddingService()
vector_service = VectorSearchService()
reranker_service = RerankerService()


# Generate query embedding once.
query_embedding = embedding_service.embed_query(question)


# Warm-up: exclude initial model/runtime overhead from measurements.
warmup_documents = vector_service.search(
    query_embedding=query_embedding,
    document_ids=document_ids,
    top_k=1,
    similarity_threshold=None,
)

if warmup_documents:
    reranker_service.rerank(
        query=question,
        documents=warmup_documents,
        top_k=1,
    )


results = []


for candidate_k in candidate_sizes:
    retrieval_times = []
    reranking_times = []
    total_times = []
    final_results = []

    for trial in range(num_trials):

        # Stage 1: Semantic retrieval
        start = perf_counter()

        candidate_documents = vector_service.search(
            query_embedding=query_embedding,
            document_ids=document_ids,
            top_k=candidate_k,
            similarity_threshold=None,
        )

        retrieval_ms = (perf_counter() - start) * 1000

        retrieval_times.append(retrieval_ms)

        # Stage 2: Reranking (only when candidate pool > final top K)
        if candidate_k > final_top_k:
            start = perf_counter()

            reranked_documents = reranker_service.rerank(
                query=question,
                documents=candidate_documents,
                top_k=final_top_k,
            )

            reranking_ms = (perf_counter() - start) * 1000

            selected_documents = reranked_documents

        else:
            reranking_ms = 0
            selected_documents = candidate_documents[:final_top_k]

        reranking_times.append(reranking_ms)

        total_ms = retrieval_ms + reranking_ms
        total_times.append(total_ms)

        # Save the final result from the last trial.
        if trial == num_trials - 1:
            final_results = selected_documents

    results.append({
        "candidate_k": candidate_k,
        "retrieval_ms": median(retrieval_times),
        "reranking_ms": median(reranking_times),
        "total_ms": median(total_times),
        "documents": final_results,
    })


# Display latency comparison.
print("\n========== LATENCY COMPARISON ==========")

print(
    f"{'Candidates':<12}"
    f"{'Retrieval(ms)':<17}"
    f"{'Reranking(ms)':<17}"
    f"{'Total(ms)':<12}"
)

for result in results:
    print(
        f"{result['candidate_k']:<12}"
        f"{result['retrieval_ms']:<17.2f}"
        f"{result['reranking_ms']:<17.2f}"
        f"{result['total_ms']:<12.2f}"
    )


# Display final top-K results for each configuration.
print("\n========== FINAL TOP-K RESULTS ==========")

for result in results:
    print(f"\nCandidate pool: {result['candidate_k']}")

    for rank, document in enumerate(result["documents"], start=1):
        print({
            "rank": rank,
            "chunk_id": document["id"],
            "page": document["page_number"],
            "similarity": round(document["similarity"], 4),
            "rerank_score": (
                round(document["rerank_score"], 4)
                if "rerank_score" in document
                else None
            ),
        })
