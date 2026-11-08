import logging
from uuid import UUID

import psycopg
from pgvector.psycopg import register_vector

from app.config import settings


logger = logging.getLogger(__name__)


class VectorSearchService:

    def search(
        self,
        query_embedding,
        document_ids: list[UUID],
        top_k: int = 3,
        similarity_threshold: float | None = None,
        min_page: int | None = None,
        max_page: int | None = None,
    ) -> list[dict]:

        if not document_ids:
            return []

        logger.info(
            (
                "Vector search started: top_k=%s, "
                "similarity_threshold=%s, min_page=%s, max_page=%s"
            ),
            top_k,
            similarity_threshold,
            min_page,
            max_page,
        )

        # Build the WHERE conditions dynamically.
        conditions = [
            "embedding IS NOT NULL",
            "document_id = ANY(%s)"
        ]

        # The first parameter belongs to document_id = ANY(%s).
        where_params = [document_ids]

        if min_page is not None:
            conditions.append("page_number >= %s")
            where_params.append(min_page)

        if max_page is not None:
            conditions.append("page_number <= %s")
            where_params.append(max_page)

        if similarity_threshold is not None:
            conditions.append(
                "(1 - (embedding <=> %s)) >= %s"
            )
            where_params.extend([
                query_embedding,
                similarity_threshold
            ])

        where_clause = " AND ".join(conditions)

        sql = f"""
            SELECT
                id,
                content,
                document_id,
                file_name,
                page_number,
                chunk_index,
                embedding <=> %s AS cosine_distance
            FROM document_chunks
            WHERE {where_clause}
            ORDER BY embedding <=> %s ASC
            LIMIT %s;
        """

        # SQL placeholder order:
        # 1. SELECT cosine distance
        # 2. WHERE conditions
        # 3. ORDER BY cosine distance
        # 4. LIMIT
        params = [
            query_embedding,
            *where_params,
            query_embedding,
            top_k
        ]

        with psycopg.connect(settings.database_url) as connection:
            register_vector(connection)

            with connection.cursor() as cursor:
                cursor.execute(sql, params)
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
                cosine_distance,
            ) = row

            similarity = 1 - float(cosine_distance)

            results.append({
                "id": chunk_id,
                "content": content,
                "document_id": document_id,
                "file_name": file_name,
                "page_number": page_number,
                "chunk_index": chunk_index,
                "similarity": similarity,
            })

        logger.info(
            (
                "Vector search completed: top_k=%s, threshold=%s, "
                "min_page=%s, max_page=%s, results=%s"
            ),
            top_k,
            similarity_threshold,
            min_page,
            max_page,
            len(results),
        )

        for result in results:
            logger.info(
                (
                    "Retrieved chunk: id=%s, file=%s, page=%s, "
                    "chunk=%s, similarity=%.4f"
                ),
                result["id"],
                result["file_name"],
                result["page_number"],
                result["chunk_index"],
                result["similarity"],
            )

        return results