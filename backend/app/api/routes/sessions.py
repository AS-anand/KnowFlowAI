from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    status
)

from app.api.dependencies import get_current_user

from app.schemas.session import (
    SessionCreateRequest,
    SessionResponse
)

from app.schemas.message import MessageResponse

from app.services.session_service import (
    create_session,
    get_user_sessions,
    get_session_by_id,
    delete_session
)

from app.services.message_service import get_session_messages

from app.schemas.session_document import (
    AttachDocumentRequest,
    SessionDocumentResponse
)

from app.services.session_service import (
    attach_document_to_session,
    SessionNotFoundError,
    DocumentNotFoundError,
    DocumentNotReadyError,
    DocumentAlreadyAttachedError
)

from app.schemas.session_document import SessionDocumentListItem
from app.services.session_service import get_session_documents

from app.services.session_service import (
    remove_document_from_session,
    DocumentNotAttachedError
)


router = APIRouter(
    prefix="/api/v1/sessions",
    tags=["Sessions"]
)


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_session(
    request: SessionCreateRequest,
    current_user: dict = Depends(get_current_user)
) -> SessionResponse:

    user_id = UUID(current_user["id"])

    return create_session(
        user_id=user_id,
        session_data=request
    )


@router.get(
    "",
    response_model=list[SessionResponse]
)
def list_user_sessions(
    current_user: dict = Depends(get_current_user)
) -> list[SessionResponse]:

    user_id = UUID(current_user["id"])

    return get_user_sessions(user_id=user_id)


@router.get(
    "/{session_id}",
    response_model=SessionResponse
)
def get_session_details(
    session_id: UUID,
    current_user: dict = Depends(get_current_user)
) -> SessionResponse:

    user_id = UUID(current_user["id"])

    session = get_session_by_id(
        session_id=session_id,
        user_id=user_id
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return session


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_user_session(
    session_id: UUID,
    current_user: dict = Depends(get_current_user)
) -> Response:

    user_id = UUID(current_user["id"])

    deleted = delete_session(
        session_id=session_id,
        user_id=user_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{session_id}/messages",
    response_model=list[MessageResponse]
)
def list_session_messages(
    session_id: UUID,
    current_user: dict = Depends(get_current_user)
) -> list[MessageResponse]:

    user_id = UUID(current_user["id"])

    messages = get_session_messages(
        session_id=session_id,
        user_id=user_id
    )

    if messages is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return messages

@router.post(
    "/{session_id}/documents",
    response_model=SessionDocumentResponse,
    status_code=status.HTTP_201_CREATED
)
def attach_document(
    session_id: UUID,
    request: AttachDocumentRequest,
    current_user: dict = Depends(get_current_user)
) -> SessionDocumentResponse:

    try:
        result = attach_document_to_session(
            session_id=session_id,
            document_id=request.document_id,
            user_id=current_user["id"]
        )

        return SessionDocumentResponse(**result)

    except SessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc

    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc

    except DocumentNotReadyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        ) from exc

    except DocumentAlreadyAttachedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        ) from exc

@router.get(
    "/{session_id}/documents",
    response_model=list[SessionDocumentListItem]
)
def list_session_documents(
    session_id: UUID,
    current_user: dict = Depends(get_current_user)
) -> list[SessionDocumentListItem]:

    documents = get_session_documents(
        session_id=session_id,
        user_id=current_user["id"]
    )

    if documents is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return [
        SessionDocumentListItem(**document)
        for document in documents
    ]


@router.delete(
    "/{session_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def detach_document(
    session_id: UUID,
    document_id: UUID,
    current_user: dict = Depends(get_current_user)
) -> None:

    try:
        remove_document_from_session(
            session_id=session_id,
            document_id=document_id,
            user_id=current_user["id"]
        )

    except SessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc

    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc

    except DocumentNotAttachedError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc

