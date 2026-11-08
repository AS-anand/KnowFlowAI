
import logging
from uuid import UUID

from app.services.embedding_service import EmbeddingService
from app.services.keyword_search_service import KeywordSearchService
from app.services.vector_search_service import VectorSearchService


logger = logging.getLogger(__name__)


class HybridSearchService:

    def __init__(
        self,
        embedding_service: EmbeddingService,
        keyword_search_service: KeywordSearchService,
        vector_search_service: VectorSearchService,
    ):
        self.embedding_service = embedding_service
        self.keyword_search_service = keyword_search_service
        self.vector_search_service = vector_search_service

    def search(
        self,
        query: str,
        document_ids: list[UUID],
        top_k: int = 5,
        rrf_k: int = 60,
    ) -> list[dict]:

        if not document_ids or not query.strip():
            return []

        if top_k < 1 or rrf_k < 1:
            raise ValueError("top_k and rrf_k must be positive")

        # Retrieve a larger candidate set from both methods.
        candidate_k = top_k * 2

        logger.info(
            "Hybrid search started: top_k=%s, candidate_k=%s",
            top_k,
            candidate_k,
        )

        # 1. Keyword retrieval
        keyword_results = self.keyword_search_service.search(
            query=query,
            document_ids=document_ids,
            top_k=candidate_k,
        )

        # 2. Semantic retrieval
        query_embedding = self.embedding_service.embed_query(query)

        semantic_results = self.vector_search_service.search(
            query_embedding=query_embedding,
            document_ids=document_ids,
            top_k=candidate_k,
            similarity_threshold=None,
        )

        # 3. Merge results using Reciprocal Rank Fusion.
        fused_results = {}

        def add_results(results, method):

            for rank, result in enumerate(results, start=1):

                chunk_id = result["id"]

                if chunk_id not in fused_results:
                    fused_results[chunk_id] = {
                        **result,
                        "rrf_score": 0.0,
                        "keyword_rank": None,
                        "semantic_rank": None,
                        "retrieval_methods": [],
                    }

                fused = fused_results[chunk_id]

                fused["rrf_score"] += 1 / (rrf_k + rank)

                fused[f"{method}_rank"] = rank
                fused["retrieval_methods"].append(method)

                # Preserve the original fields from both retrieval methods.
                for key, value in result.items():
                    if key not in fused or fused[key] is None:
                        fused[key] = value

        add_results(keyword_results, "keyword")
        add_results(semantic_results, "semantic")

        # 4. Sort by combined RRF score.
        ranked_results = sorted(
            fused_results.values(),
            key=lambda item: (-item["rrf_score"], str(item["id"])),
        )

        final_results = ranked_results[:top_k]

        logger.info(
            "Hybrid search completed: keyword=%s, semantic=%s, fused=%s",
            len(keyword_results),
            len(semantic_results),
            len(final_results),
        )

        for rank, result in enumerate(final_results, start=1):
            logger.info(
                (
                    "Hybrid result: rank=%s, id=%s, page=%s, "
                    "rrf_score=%.6f, keyword_rank=%s, semantic_rank=%s"
                ),
                rank,
                result["id"],
                result["page_number"],
                result["rrf_score"],
                result["keyword_rank"],
                result["semantic_rank"],
            )

        return final_results
