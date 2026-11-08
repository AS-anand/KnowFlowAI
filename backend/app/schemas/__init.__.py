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
                (user_id,)
            )

            rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "title": row[1],
            "created_at": row[2],
            "updated_at": row[3]
        }
        for row in rows
    ]