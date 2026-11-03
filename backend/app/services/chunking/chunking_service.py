
from dataclasses import dataclass

from app.models.document_chunk import DocumentChunk
from app.models.parsed_document import ParsedPage


@dataclass
class TextChunk:
    chunk_index: int
    content: str


class ChunkingService:
    SEPARATORS = ["\n\n", "\n", ". ", "? ", "! ", " "]

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        if chunk_size <= 0:
            raise ValueError("Chunk size must be greater than zero")

        if chunk_overlap < 0:
            raise ValueError("Chunk overlap cannot be negative")

        if chunk_overlap >= chunk_size:
            raise ValueError("Chunk overlap must be smaller than chunk size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[TextChunk]:
        text = text.strip()

        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            hard_end = min(start + self.chunk_size, len(text))

            if hard_end == len(text):
                end = hard_end
            else:
                end = self._find_boundary(
                    text,
                    start,
                    hard_end,
                    self.SEPARATORS
                )

            # Always make progress, even with unusual input.
            if end <= start:
                end = hard_end

            content = text[start:end].strip()

            if content:
                chunks.append(
                    TextChunk(
                        chunk_index=len(chunks),
                        content=content
                    )
                )

            if end == len(text):
                break

            # Start the next chunk before the previous one ended.
            next_start = max(start + 1, end - self.chunk_overlap)

            # Prefer beginning the next chunk at a word boundary.
            whitespace_position = text.find(" ", next_start, end)

            if whitespace_position != -1:
                next_start = whitespace_position + 1

            start = next_start

        return chunks

    def _find_boundary(
        self,
        text: str,
        start: int,
        hard_end: int,
        separators: list[str]
    ) -> int:
        if not separators:
            return hard_end

        separator = separators[0]

        boundary = text.rfind(separator, start + 1, hard_end)

        if boundary != -1:
            return boundary + len(separator)

        # Try the next, less-preferred separator.
        return self._find_boundary(
            text,
            start,
            hard_end,
            separators[1:]
        )

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
