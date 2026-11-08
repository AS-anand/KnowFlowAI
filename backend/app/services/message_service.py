
from typing import Literal
from uuid import UUID

import psycopg

from app.config import settings


MessageRole = Literal["user", "assistant"]


def create_message(
    session_id: UUID,
    user_id: UUID,
    role: MessageRole,
    content: str
) -> dict:

    with psycopg.connect(settings.database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO messages (
                    session_id,
                    role,
                    content
                )
                SELECT
                    id,
                    %s,
                    %s
                FROM sessions
                WHERE id = %s
                  AND user_id = %s
                RETURNING id, session_id, role, content, created_at;
                """,
                (role, content, session_id, user_id)
            )

            row = cursor.fetchone()

    if row is None:
        raise ValueError("Session not found")

    return {
        "id": row[0],
        "session_id": row[1],
        "role": row[2],
        "content": row[3],
        "created_at": row[4]
    }


def get_session_messages(
    session_id: UUID,
    user_id: UUID
) -> list[dict] | None:

    with psycopg.connect(settings.database_url) as connection:
        with connection.cursor() as cursor:

            # First, verify session ownership.
            cursor.execute(
                """
                SELECT id
                FROM sessions
                WHERE id = %s
                  AND user_id = %s;
                """,
                (session_id, user_id)
            )

            session = cursor.fetchone()

            if session is None:
                return None

            # Retrieve messages in chronological order.
            cursor.execute(
                """
                SELECT id, session_id, role, content, created_at
                FROM messages
                WHERE session_id = %s
                ORDER BY created_at ASC, id ASC;
                """,
                (session_id,)
            )

            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "session_id": row[1],
            "role": row[2],
            "content": row[3],
            "created_at": row[4]
        }
        for row in rows
    ]