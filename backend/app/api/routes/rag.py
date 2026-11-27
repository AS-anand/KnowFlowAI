
import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_rag_service, get_current_user
from app.models.rag_models import RAGQueryRequest, RAGResponse
from app.services.rag_service import RAGService
from app.services.message_service import (
    create_message,
    get_recent_session_messages,
    select_conversation_history,
)


router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])


@router.post("/query", response_model=RAGResponse)
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

        # 2. Retrieve previous messages BEFORE saving
        #    the current question.
        previous_messages = await asyncio.to_thread(
            get_recent_session_messages,
            request.session_id,
            user_id,
            10
        )

        if previous_messages is None:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )

        # 3. Select history within the character budget.
        conversation_history = select_conversation_history(
            previous_messages,
            max_messages=10,
            max_characters=8000
        )

        # 4. Persist the current user question.
        await asyncio.to_thread(
            create_message,
            session_id=request.session_id,
            user_id=user_id,
            role="user",
            content=request.question
        )

        # 5. Execute conversation-aware RAG.
        response = await rag_service.query(
            session_id=request.session_id,
            user_id=user_id,
            question=request.question,
            conversation_history=conversation_history,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            min_page=request.min_page,
            max_page=request.max_page
        )

        # 6. Persist the assistant response.
        await asyncio.to_thread(
            create_message,
            session_id=request.session_id,
            user_id=user_id,
            role="assistant",
            content=response.answer
        )

        # 7. Return response.
        return response

    except ValueError as exc:
        if str(exc) == "Session not found":
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            ) from exc

        raise
