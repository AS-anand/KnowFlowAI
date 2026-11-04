import psycopg

from app.core.password import hash_password
from app.schemas.auth import RegisterRequest
from app.config import settings


class DuplicateEmailError(Exception):
    pass


def register_user(user_data: RegisterRequest) -> dict:
    password_hash = hash_password(user_data.password)

    with psycopg.connect(settings.database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (name, email, password_hash)
                VALUES (%s, %s, %s)
                ON CONFLICT (email) DO NOTHING
                RETURNING id, name, email, created_at;
                """,
                (
                    user_data.name,
                    str(user_data.email),
                    password_hash
                )
            )

            user = cursor.fetchone()

            if user is None:
                raise DuplicateEmailError(
                    "Email already registered"
                )

            return {
                "id": str(user[0]),
                "name": user[1],
                "email": user[2],
                "created_at": user[3].isoformat()
            }