
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from app.api.dependencies import (
    get_rag_service,
    get_current_user
)

from app.models.rag_models import (
    RAGQueryRequest,
    RAGResponse
)

from app.services.rag_service import RAGService
from app.services.message_service import create_message
import asyncio


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
    current_user: dict = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service)
) -> RAGResponse:

    user_id = UUID(current_user["id"])

    try:
        # 1. Validate session ownership.
        await asyncio.to_thread(
            rag_service.validate_session_ownership,
            request.session_id,
            user_id
        )

        # 2. Persist the user's question.
        create_message(
            session_id=request.session_id,
            user_id=user_id,
            role="user",
            content=request.question
        )

        # 3. Execute the RAG pipeline.
        response = await rag_service.query(
            session_id=request.session_id,
            user_id=user_id,
            question=request.question,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            min_page=request.min_page,
            max_page=request.max_page
        )

        # 4. Persist the assistant's answer.
        create_message(
            session_id=request.session_id,
            user_id=user_id,
            role="assistant",
            content=response.answer
        )

        # 5. Return the RAG response.
        return response

    except ValueError as exc:
        if str(exc) == "Session not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            ) from exc

        raise
