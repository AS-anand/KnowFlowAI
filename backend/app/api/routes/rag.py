
from fastapi import APIRouter, Depends

from app.api.dependencies import get_rag_service

from app.models.rag_models import (
    RAGQueryRequest,
    RAGResponse
)

from app.services.rag_service import RAGService


router = APIRouter(
    prefix="/api/v1/rag",
    tags=["RAG"]
)


@router.post(
    "/query",
    response_model=RAGResponse
)
async def query_documents(
    request: RAGQueryRequest,
    rag_service: RAGService = Depends(get_rag_service)
) -> RAGResponse:

    return await rag_service.query(
        question=request.question,
        top_k=request.top_k
    )
