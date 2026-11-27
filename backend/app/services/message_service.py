
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


def get_recent_session_messages(
    session_id: UUID,
    user_id: UUID,
    limit: int = 10
) -> list[dict] | None:
    """
    Retrieve the latest messages for an authorized session.

    Returns:
        None: Session does not exist or does not belong to the user.
        []: Session exists but has no messages.
        list[dict]: Latest messages in chronological order.
    """
    if limit < 1:
        raise ValueError("limit must be positive")

    with psycopg.connect(settings.database_url) as connection:
        with connection.cursor() as cursor:
            # Verify session ownership.
            cursor.execute(
                """
                SELECT id
                FROM sessions
                WHERE id = %s
                  AND user_id = %s;
                """,
                (session_id, user_id)
            )

            if cursor.fetchone() is None:
                return None

            # Fetch newest messages first, then reverse them.
            cursor.execute(
                """
                SELECT id, session_id, role, content, created_at
                FROM messages
                WHERE session_id = %s
                ORDER BY created_at DESC, id DESC
                LIMIT %s;
                """,
                (session_id, limit)
            )

            rows = cursor.fetchall()

    messages = [
        {
            "id": row[0],
            "session_id": row[1],
            "role": row[2],
            "content": row[3],
            "created_at": row[4]
        }
        for row in rows
    ]

    messages.reverse()

    return messages


def select_conversation_history(
    messages: list[dict],
    max_messages: int = 10,
    max_characters: int = 8000
) -> list[dict]:
    """
    Select the most recent messages within a character budget.

    Messages are returned in chronological order.
    Older messages are discarded first.
    """
    if max_messages < 1 or max_characters < 1:
        raise ValueError("History limits must be positive")

    selected = []
    remaining_characters = max_characters

    for message in reversed(messages[-max_messages:]):
        content = message["content"]

        if not isinstance(content, str):
            continue

        if remaining_characters <= 0:
            break

        # Preserve the most recent part of an oversized message.
        if len(content) > remaining_characters:
            content = content[-remaining_characters:]

        selected.append({
            "role": message["role"],
            "content": content
        })

        remaining_characters -= len(content)

    selected.reverse()

    return selected
