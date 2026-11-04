from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.models.document_chunk import DocumentChunk
from app.models.parsed_document import ParsedPage


@dataclass
class TextChunk:
    chunk_index: int
    content: str


class ChunkingService:

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""],
            keep_separator=True
        )

    def split_text(self, text: str) -> list[TextChunk]:
        text = text.strip()

        if not text:
            return []

        split_texts = self.splitter.split_text(text)

        return [
            TextChunk(
                chunk_index=index,
                content=content
            )
            for index, content in enumerate(split_texts)
            if content.strip()
        ]

    def chunk_document_page(
        self,
        page: ParsedPage
    ) -> list[DocumentChunk]:

        text_chunks = self.split_text(page.content)

        return [
            DocumentChunk(
                chunk_index=chunk.chunk_index,
                document_id=page.document_id,
                file_name=page.file_name,
                page_number=page.page_number,
                content=chunk.content
            )
            for chunk in text_chunks
        ]