
import logging
from typing import Any

from sentence_transformers import CrossEncoder


logger = logging.getLogger(__name__)


class RerankerService:

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        batch_size: int = 16,
    ):
        if batch_size < 1:
            raise ValueError("batch_size must be positive")

        logger.info("Loading reranker model: %s", model_name)

        self.model = CrossEncoder(
            model_name,
            max_length=512,
        )

        self.batch_size = batch_size

        logger.info("Reranker model loaded successfully")

    def rerank(
        self,
        query: str,
        documents: list[dict[str, Any]],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:

        if not query.strip() or not documents:
            return []

        if top_k < 1:
            raise ValueError("top_k must be positive")

        # Each candidate must contain text to rerank.
        for document in documents:
            if not isinstance(document.get("content"), str):
                raise ValueError(
                    "Every document must contain string content"
                )

        # Create query-document pairs.
        pairs = [
            (query, document["content"])
            for document in documents
        ]

        logger.info(
            "Reranking started: candidates=%s, top_k=%s",
            len(documents),
            top_k,
        )

        # Generate relevance scores.
        scores = self.model.predict(
            pairs,
            batch_size=self.batch_size,
            show_progress_bar=False,
        )

        # Preserve all original document metadata.
        reranked_documents = []

        for document, score in zip(documents, scores):
            result = {
                **document,
                "rerank_score": float(score),
            }

            reranked_documents.append(result)

        # Sort by cross-encoder relevance score.
        reranked_documents.sort(
            key=lambda item: item["rerank_score"],
            reverse=True,
        )

        # Assign final ranking positions.
        final_results = reranked_documents[:top_k]

        for rank, result in enumerate(final_results, start=1):
            result["rerank_rank"] = rank

            logger.info(
                (
                    "Reranked result: rank=%s, id=%s, "
                    "page=%s, score=%.4f"
                ),
                rank,
                result.get("id"),
                result.get("page_number"),
                result["rerank_score"],
            )

        logger.info(
            "Reranking completed: returned=%s",
            len(final_results),
        )

        return final_results
