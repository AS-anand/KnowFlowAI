
import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

from app.config import settings


def main():
    # 1. Load the embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # 2. User's search query
    query = "What benefits does the company offer?"

    # 3. Convert query into a 384-dimensional vector
    query_embedding = model.encode(query)

    # 4. Connect to PostgreSQL
    with psycopg.connect(settings.database_url) as connection:
        register_vector(connection)

        with connection.cursor() as cursor:

            # 5. Search for the nearest document chunks
            cursor.execute(
                """
                SELECT
                    id,
                    content,
                    embedding <=> %s AS cosine_distance
                FROM document_chunks
                ORDER BY cosine_distance ASC
                LIMIT 3;
                """,
                (query_embedding,)
            )

            results = cursor.fetchall()

    # 6. Display search results
    print(f"\nUser query: {query}")
    print("\nTop 3 search results:")

    for rank, (chunk_id, content, distance) in enumerate(results, start=1):
        similarity = 1 - float(distance)

        print(f"\nRank: {rank}")
        print(f"Chunk ID: {chunk_id}")
        print(f"Similarity: {similarity:.4f}")
        print(f"Content: {content}")


if __name__ == "__main__":
    main()
