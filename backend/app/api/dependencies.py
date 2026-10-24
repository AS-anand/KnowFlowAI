from fastapi import Request

from app.services.document_summarizer import DocumentSummarizer


def get_summarizer(request: Request) -> DocumentSummarizer:
    return request.app.state.summarizer