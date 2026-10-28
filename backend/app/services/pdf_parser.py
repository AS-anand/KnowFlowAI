
from pathlib import Path
from uuid import uuid4

from pypdf import PdfReader

from app.models.parsed_document import ParsedDocument, ParsedPage


class PDFParser:

    def parse(self, file_path: str) -> ParsedDocument:
        path = Path(file_path)

        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"PDF not found: {file_path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError("Only PDF files are supported")

        reader = PdfReader(str(path))

        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported")

        document_id = str(uuid4())

        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            content = page.extract_text() or ""

            pages.append(
                ParsedPage(
                    document_id=document_id,
                    file_name=path.name,
                    page_number=page_number,
                    content=content.strip()
                )
            )

        metadata = {
            "title": reader.metadata.title if reader.metadata else None,
            "author": reader.metadata.author if reader.metadata else None,
            "subject": reader.metadata.subject if reader.metadata else None,
        }

        return ParsedDocument(
            document_id=document_id,
            file_name=path.name,
            total_pages=len(reader.pages),
            metadata=metadata,
            pages=pages
        )
