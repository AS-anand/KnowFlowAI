import logging
from uuid import UUID

import psycopg

from app.config import settings


logger = logging.getLogger(__name__)


class KeywordSearchService:

    def search(
        self,
        query: str,
        document_ids: list[UUID],
        top_k: int = 5,
    ) -> list[dict]:

        if not document_ids:
            return []

        if not query.strip():
            return []

        logger.info(
            "Keyword search started: top_k=%s, document_count=%s",
            top_k,
            len(document_ids),
        )

        sql = """
            SELECT
                id,
                content,
                document_id,
                file_name,
                page_number,
                chunk_index,
                ts_rank_cd(
                    search_vector,
                    websearch_to_tsquery('english', %s)
                ) AS rank_score
            FROM document_chunks
            WHERE search_vector @@
                websearch_to_tsquery('english', %s)
              AND document_id = ANY(%s)
            ORDER BY rank_score DESC
            LIMIT %s;
        """

        with psycopg.connect(settings.database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        query,
                        query,
                        document_ids,
                        top_k,
                    ),
                )

                rows = cursor.fetchall()

        results = []

        for row in rows:
            (
                chunk_id,
                content,
                document_id,
                file_name,
                page_number,
                chunk_index,
                rank_score,
            ) = row

            results.append({
                "id": chunk_id,
                "content": content,
                "document_id": document_id,
                "file_name": file_name,
                "page_number": page_number,
                "chunk_index": chunk_index,
                "rank_score": float(rank_score),
            })

        logger.info(
            "Keyword search completed: top_k=%s, results=%s",
            top_k,
            len(results),
        )

        for result in results:
            logger.info(
                (
                    "Keyword result: id=%s, file=%s, page=%s, "
                    "chunk=%s, rank_score=%.4f"
                ),
                result["id"],
                result["file_name"],
                result["page_number"],
                result["chunk_index"],
                result["rank_score"],
            )

        return results