class DocumentProcessingError(Exception):
    """Base exception for document processing errors."""


class DocumentNotFoundError(DocumentProcessingError):
    """Raised when the requested document does not exist."""


class UnsupportedDocumentFormatError(DocumentProcessingError):
    """Raised when the document format is not supported."""


class EmptyDocumentError(DocumentProcessingError):
    """Raised when the document contains no meaningful content."""