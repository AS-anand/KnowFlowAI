import psycopg
from pgvector.psycopg import register_vector

from app.config import settings
from app.models.parsed_document import ParsedDocument
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService


class DocumentIngestionService:

    def __init__(
        self,
        chunking_service: ChunkingService,
        embedding_service: EmbeddingService
    ):
        self.chunking_service = chunking_service
        self.embedding_service = embedding_service

    def ingest(self, document: ParsedDocument) -> int:

        # 1. Split every PDF page into chunks.
        chunks = []

        for page in document.pages:
            page_chunks = self.chunking_service.chunk_document_page(page)
            chunks.extend(page_chunks)

        if not chunks:
            raise ValueError(
                "PDF contains no extractable text. "
                "Scanned PDFs require OCR."
            )

        # 2. Generate embeddings in one batch.
        texts = [chunk.content for chunk in chunks]

        embeddings = self.embedding_service.embed_documents(texts)

        if len(embeddings) != len(chunks):
            raise ValueError("Embedding count does not match chunk count")

        # 3. Prepare database records.
        records = [
            (
                chunk.content,
                embedding,
                chunk.document_id,
                chunk.file_name,
                chunk.page_number,
                chunk.chunk_index
            )
            for chunk, embedding in zip(chunks, embeddings)
        ]

        # 4. Persist all chunks in one transaction.
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

        return len(chunks)