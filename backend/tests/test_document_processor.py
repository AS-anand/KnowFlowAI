import pytest

from app.models.document import Document
from app.services.document_processor import DocumentProcessor
from app.exceptions import (
    DocumentNotFoundError,
    UnsupportedDocumentFormatError,
    EmptyDocumentError
)


@pytest.fixture
def processor():
    return DocumentProcessor()


def test_document_word_count():

    document = Document(
        file_name="sample.txt",
        content="Python is useful for AI development"
    )

    assert document.word_count == 6


def test_document_character_count():

    document = Document(
        file_name="sample.txt",
        content="Hello World"
    )

    assert document.character_count == 11


def test_document_paragraph_count():

    document = Document(
        file_name="sample.txt",
        content="First paragraph\n\nSecond paragraph"
    )

    assert document.paragraph_count == 2


def test_clean_text(processor):

    raw_text = (
        "  First line  \n"
        "Second line\n\n"
        "  Third paragraph  "
    )

    result = processor.clean_text(raw_text)

    expected = "First line Second line\n\nThird paragraph"

    assert result == expected


def test_process_valid_document(processor, tmp_path):

    file_path = tmp_path / "sample.txt"

    file_path.write_text(
        "Python is useful for AI applications",
        encoding="utf-8"
    )

    result = processor.process_document(str(file_path))

    assert result["file_name"] == "sample.txt"
    assert result["metadata"]["word_count"] == 6
    assert result["metadata"]["paragraph_count"] == 1


def test_missing_document(processor, tmp_path):

    file_path = tmp_path / "missing.txt"

    with pytest.raises(DocumentNotFoundError):
        processor.process_document(str(file_path))


def test_unsupported_document_format(processor, tmp_path):

    file_path = tmp_path / "sample.pdf"

    file_path.write_text(
        "Sample PDF content",
        encoding="utf-8"
    )

    with pytest.raises(UnsupportedDocumentFormatError):
        processor.process_document(str(file_path))


def test_empty_document(processor, tmp_path):

    file_path = tmp_path / "empty.txt"

    file_path.write_text(
        "   \n\n   ",
        encoding="utf-8"
    )

    with pytest.raises(EmptyDocumentError):
        processor.process_document(str(file_path))