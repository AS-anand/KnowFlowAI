
import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

from app.config import settings


def main():
    # 1. Load the embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # 2. Sample document chunks
    documents = [
        "Employees receive 20 paid leave days annually.",
        "All leave requests require approval from the reporting manager.",
        "Employees can access their payslips through the HR portal.",
        "Unused leave can be carried forward up to five days.",
        "The company provides health insurance to employees."
    ]

    # 3. Generate embeddings
    embeddings = model.encode(documents)

    # 4. Connect to PostgreSQL
    with psycopg.connect(settings.database_url) as connection:

        # Register pgvector support with Psycopg
        register_vector(connection)

        # 5. Insert document chunks and embeddings
        with connection.cursor() as cursor:
            for document, embedding in zip(documents, embeddings):
                cursor.execute(
                    """
                    INSERT INTO document_chunks (content, embedding)
                    VALUES (%s, %s)
                    """,
                    (document, embedding)
                )

        connection.commit()

    print(f"Successfully stored {len(documents)} document chunks!")


if __name__ == "__main__":
    main()
