import psycopg
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError

from app.services.document_summarizer import DocumentSummarizer
from app.services.rag_service import RAGService
from app.config import settings
from app.core.jwt import verify_access_token


bearer_scheme = HTTPBearer(auto_error=False)


def get_summarizer(request: Request) -> DocumentSummarizer:
    return request.app.state.summarizer


def get_rag_service(request: Request) -> RAGService:
    return request.app.state.rag_service


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict:

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        user_id = verify_access_token(credentials.credentials)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    with psycopg.connect(settings.database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, email, created_at
                FROM users
                WHERE id = %s;
                """,
                (user_id,)
            )

            user = cursor.fetchone()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {
        "id": str(user[0]),
        "name": user[1],
        "email": user[2],
        "created_at": user[3].isoformat()
    }