from fastapi import Request

from app.services.document_summarizer import DocumentSummarizer
from app.services.rag_service import RAGService


def get_summarizer(request: Request) -> DocumentSummarizer:
    return request.app.state.summarizer


def get_rag_service(request: Request) -> RAGService:
    return request.app.state.rag_service
