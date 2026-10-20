from pathlib import Path

from app.services.document_processor import DocumentProcessor
from app.exceptions import DocumentProcessingError


def main():

    backend_root = Path(__file__).resolve().parent.parent

    sample_file = (
        backend_root
        / "sample_documents"
        / "sample.txt"
    )

    processor = DocumentProcessor()

    try:
        result = processor.process_document(str(sample_file))

        print("Document processed successfully!")
        print(result)

    except DocumentProcessingError as exc:
        print(f"Document processing failed: {exc}")


if __name__ == "__main__":
    main()