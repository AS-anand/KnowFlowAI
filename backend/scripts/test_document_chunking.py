
from pathlib import Path

from app.services.pdf_parser import PDFParser
from app.services.chunking.chunking_service import ChunkingService


def main():
    backend_root = Path(__file__).resolve().parent.parent
    pdf_path = backend_root / "sample_documents" / "sample.pdf"

    parser = PDFParser()
    document = parser.parse(str(pdf_path))

    # Inspect the original extracted text before chunking.
    for page in document.pages:
        print(f"\n--- RAW PAGE {page.page_number} ---")
        print(repr(page.content))

    chunker = ChunkingService(
        chunk_size=500,
        chunk_overlap=100
    )

    all_chunks = []

    for page in document.pages:
        page_chunks = chunker.chunk_document_page(page)
        all_chunks.extend(page_chunks)

    for chunk in all_chunks:
        assert len(chunk.content) <= 500, (
            f"Chunk exceeds limit: {len(chunk.content)}"
        )

        assert chunk.content.strip(), "Empty chunk found"

    print("\nAll chunk validation checks passed!")

    print("\nDocument ID:", document.document_id)
    print("Total pages:", document.total_pages)
    print("Total chunks:", len(all_chunks))

    for chunk in all_chunks:
        print("\n----------------------------")
        print("Chunk index:", chunk.chunk_index)
        print("Document ID:", chunk.document_id)
        print("File name:", chunk.file_name)
        print("Page number:", chunk.page_number)
        print("Content:", chunk.content)


if __name__ == "__main__":
    main()
