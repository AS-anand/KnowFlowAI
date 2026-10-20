from pathlib import Path

from app.exceptions import (
    DocumentNotFoundError,
    UnsupportedDocumentFormatError,
    EmptyDocumentError,
    DocumentProcessingError
)

from app.models.document import Document


class DocumentProcessor:

    def clean_text(self, text: str) -> str:

        raw_paragraphs = text.split("\n\n")

        cleaned_paragraphs = [
            " ".join(
                line.strip()
                for line in paragraph.splitlines()
                if line.strip()
            )
            for paragraph in raw_paragraphs
            if paragraph.strip()
        ]

        return "\n\n".join(cleaned_paragraphs)

    def read_document(self, file_path: str) -> Document:

        path = Path(file_path)

        if not path.exists():
            raise DocumentNotFoundError(
                f"Document not found: {file_path}"
            )

        if not path.is_file():
            raise DocumentProcessingError(
                f"Path is not a file: {file_path}"
            )

        if path.suffix.lower() not in Document.supported_formats:
            raise UnsupportedDocumentFormatError(
                f"Unsupported document format: {path.suffix}"
            )

        try:
            raw_text = path.read_text(encoding="utf-8")

        except UnicodeDecodeError as exc:
            raise DocumentProcessingError(
                f"Unable to decode document: {path.name}"
            ) from exc

        cleaned_content = self.clean_text(raw_text)

        if not cleaned_content:
            raise EmptyDocumentError(
                f"Document is empty: {path.name}"
            )

        return Document(
            file_name=path.name,
            content=cleaned_content
        )

    def process_document(self, file_path: str) -> dict:

        document = self.read_document(file_path)

        return {
            "file_name": document.file_name,
            "content": document.content,
            "metadata": document.get_summary()
        }