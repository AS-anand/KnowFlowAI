
from pathlib import Path

from app.services.pdf_parser import PDFParser


def main():
    backend_root = Path(__file__).resolve().parent.parent

    pdf_path = backend_root / "sample_documents" / "sample.pdf"

    parser = PDFParser()
    document = parser.parse(str(pdf_path))

    print("Document ID:", document.document_id)
    print("File name:", document.file_name)
    print("Total pages:", document.total_pages)
    print("PDF metadata:", document.metadata)

    for page in document.pages:
        print(f"\n--- Page {page.page_number} ---")
        print(page.content)


if __name__ == "__main__":
    main()
