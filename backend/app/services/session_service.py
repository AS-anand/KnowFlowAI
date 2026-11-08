import psycopg
from uuid import UUID

from app.config import settings
from app.schemas.session import SessionCreateRequest


class DocumentNotAttachedError(Exception):
    pass


def create_session(user_id: UUID, session_data: SessionCreateRequest) -> dict:
    with psycopg.connect(settings.database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sessions (user_id, title)
                VALUES (%s, %s)
                RETURNING id, title, created_at, updated_at;
                """,
                (user_id, session_data.title),
            )
            session = cursor.fetchone()

    return {
        "id": session[0],
        "title": session[1],
        "created_at": session[2],
        "updated_at": session[3],
    }


def get_user_sessions(user_id: UUID) -> list[dict]:
    with psycopg.connect(settings.database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, created_at, updated_at
                FROM sessions
                WHERE user_id = %s
                ORDER BY updated_at DESC;
                """,
                (user_id,),
            )

            rows = cursor.fetchall()

    return [
        {"id": row[0], "title": row[1], "created_at": row[2], "updated_at": row[3]}
        for row in rows
    ]


def get_session_by_id(session_id: UUID, user_id: UUID) -> dict | None:
    with psycopg.connect(settings.database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, title, created_at, updated_at
                FROM sessions
                WHERE id = %s
                  AND user_id = %s;
                """,
                (session_id, user_id),
            )

            row = cursor.fetchone()

    if row is None:
        return None

    return {"id": row[0], "title": row[1], "created_at": row[2], "updated_at": row[3]}


def delete_session(session_id: UUID, user_id: UUID) -> bool:
    with psycopg.connect(settings.database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM sessions
                WHERE id = %s
                  AND user_id = %s
                RETURNING id;
                """,
                (session_id, user_id),
            )

            deleted_session = cursor.fetchone()

    return deleted_session is not None


import psycopg
from uuid import UUID

from app.config import settings


class SessionNotFoundError(Exception):
    pass


class DocumentNotFoundError(Exception):
    pass


class DocumentNotReadyError(Exception):
    pass


class DocumentAlreadyAttachedError(Exception):
    pass


def attach_document_to_session(
    session_id: UUID, document_id: UUID, user_id: UUID
) -> dict:

    with psycopg.connect(settings.database_url) as connection:
        with connection.cursor() as cursor:

            # 1. Verify that the session belongs to the user.
            cursor.execute(
                """
                SELECT id
                FROM sessions
                WHERE id = %s AND user_id = %s;
                """,
                (session_id, user_id),
            )

            if cursor.fetchone() is None:
                raise SessionNotFoundError("Session not found")

            # 2. Verify that the document belongs to the same user.
            cursor.execute(
                """
                SELECT id, status
                FROM documents
                WHERE id = %s AND user_id = %s;
                """,
                (document_id, user_id),
            )

            document = cursor.fetchone()

            if document is None:
                raise DocumentNotFoundError("Document not found")

            if document[1] != "completed":
                raise DocumentNotReadyError("Only completed documents can be attached")

            # 3. Create the association.
            # The composite primary key also protects against duplicates.
            cursor.execute(
                """
                INSERT INTO session_documents (
                    session_id,
                    document_id
                )
                VALUES (%s, %s)
                ON CONFLICT (session_id, document_id) DO NOTHING
                RETURNING session_id, document_id, attached_at;
                """,
                (session_id, document_id),
            )

            association = cursor.fetchone()

            if association is None:
                raise DocumentAlreadyAttachedError(
                    "Document is already attached to this session"
                )

    return {
        "session_id": association[0],
        "document_id": association[1],
        "attached_at": association[2],
    }


def get_session_documents(session_id: UUID, user_id: UUID) -> list[dict] | None:

    with psycopg.connect(settings.database_url) as connection:
        with connection.cursor() as cursor:

            # 1. Verify session ownership.
            cursor.execute(
                """
                SELECT id
                FROM sessions
                WHERE id = %s AND user_id = %s;
                """,
                (session_id, user_id),
            )

            if cursor.fetchone() is None:
                return None

            # 2. Retrieve documents attached to this session.
            cursor.execute(
                """
                SELECT
                    d.id,
                    d.file_name,
                    d.status,
                    sd.attached_at
                FROM session_documents sd
                JOIN documents d
                    ON d.id = sd.document_id
                WHERE
                    sd.session_id = %s
                    AND d.user_id = %s
                ORDER BY sd.attached_at DESC;
                """,
                (session_id, user_id),
            )

            rows = cursor.fetchall()

    return [
        {
            "document_id": row[0],
            "file_name": row[1],
            "status": row[2],
            "attached_at": row[3],
        }
        for row in rows
    ]


def remove_document_from_session(
    session_id: UUID, document_id: UUID, user_id: UUID
) -> bool:

    with psycopg.connect(settings.database_url) as connection:
        with connection.cursor() as cursor:

            # 1. Verify session ownership.
            cursor.execute(
                """
                SELECT id
                FROM sessions
                WHERE id = %s AND user_id = %s;
                """,
                (session_id, user_id),
            )

            if cursor.fetchone() is None:
                raise SessionNotFoundError("Session not found")

            # 2. Verify document ownership.
            cursor.execute(
                """
                SELECT id
                FROM documents
                WHERE id = %s AND user_id = %s;
                """,
                (document_id, user_id),
            )

            if cursor.fetchone() is None:
                raise DocumentNotFoundError("Document not found")

            # 3. Remove only the association.
            cursor.execute(
                """
                DELETE FROM session_documents
                WHERE session_id = %s
                  AND document_id = %s
                  AND user_id = %s
                RETURNING session_id;
                """,
                (session_id, document_id, user_id),
            )

            if cursor.fetchone() is None:
                raise DocumentNotAttachedError(
                    "Document is not attached to this session"
                )

    return True
