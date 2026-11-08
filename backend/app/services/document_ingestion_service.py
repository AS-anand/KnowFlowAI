
import logging
from uuid import UUID

import psycopg
from pgvector.psycopg import register_vector

from app.config import settings
from app.models.parsed_document import ParsedDocument
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService


logger = logging.getLogger(__name__)


class DocumentIngestionService:

    def __init__(
        self,
        chunking_service: ChunkingService,
        embedding_service: EmbeddingService
    ):
        self.chunking_service = chunking_service
        self.embedding_service = embedding_service

    def ingest(
        self,
        document: ParsedDocument,
        user_id: UUID
    ) -> int:

        document_id = UUID(document.document_id)

        # 1. Create and commit the document record.
        # This is a separate transaction so the record survives
        # if subsequent ingestion steps fail.

        with psycopg.connect(settings.database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO documents (
                        id,
                        user_id,
                        file_name,
                        status
                    )
                    VALUES (%s, %s, %s, 'processing');
                    """,
                    (
                        document_id,
                        user_id,
                        document.file_name
                    )
                )

        try:
            # 2. Split every PDF page into chunks.

            chunks = []

            for page in document.pages:
                page_chunks = self.chunking_service.chunk_document_page(page)
                chunks.extend(page_chunks)

            if not chunks:
                raise ValueError(
                    "PDF contains no extractable text. "
                    "Scanned PDFs require OCR."
                )

            # 3. Generate embeddings in one batch.

            texts = [chunk.content for chunk in chunks]

            embeddings = self.embedding_service.embed_documents(texts)

            if len(embeddings) != len(chunks):
                raise ValueError(
                    "Embedding count does not match chunk count"
                )

            # 4. Prepare database records.

            records = [
                (
                    chunk.content,
                    embedding,
                    document_id,
                    document.file_name,
                    chunk.page_number,
                    chunk.chunk_index
                )
                for chunk, embedding in zip(chunks, embeddings)
            ]

            # 5. Persist chunks and mark document completed.
            # Both operations happen in the same transaction.

            with psycopg.connect(settings.database_url) as connection:
                register_vector(connection)

                with connection.cursor() as cursor:
                    cursor.executemany(
                        """
                        INSERT INTO document_chunks (
                            content,
                            embedding,
                            document_id,
                            file_name,
                            page_number,
                            chunk_index
                        )
                        VALUES (%s, %s, %s, %s, %s, %s);
                        """,
                        records
                    )

                    cursor.execute(
                        """
                        UPDATE documents
                        SET status = 'completed',
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                          AND user_id = %s;
                        """,
                        (document_id, user_id)
                    )

                    if cursor.rowcount != 1:
                        raise ValueError(
                            "Document record not found for this owner"
                        )

            return len(chunks)

        except Exception:
            # 6. If ingestion fails, retain the document record
            # and mark it as failed.

            try:
                with psycopg.connect(settings.database_url) as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            UPDATE documents
                            SET status = 'failed',
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = %s
                              AND user_id = %s;
                            """,
                            (document_id, user_id)
                        )
            except Exception:
                logger.exception(
                    "Failed to update document status to failed: %s",
                    document_id
                )

            raise
