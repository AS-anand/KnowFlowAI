
import psycopg

from pgvector.psycopg import register_vector

from app.config import settings


class VectorSearchService:

    def search(self, query_embedding, top_k: int = 3) -> list[dict]:

        with psycopg.connect(settings.database_url) as connection:
            register_vector(connection)

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        content,
                        document_id,
                        file_name,
                        page_number,
                        chunk_index,
                        embedding <=> %s AS cosine_distance
                    FROM document_chunks
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> %s ASC
                    LIMIT %s;
                    """,
                    (query_embedding, query_embedding, top_k)
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
                cosine_distance
            ) = row

            similarity = 1 - float(cosine_distance)

            results.append({
                "id": chunk_id,
                "content": content,
                "document_id": document_id,
                "file_name": file_name,
                "page_number": page_number,
                "chunk_index": chunk_index,
                "similarity": similarity
            })

        return results
