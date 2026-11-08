import psycopg

from app.core.password import hash_password
from app.schemas.auth import RegisterRequest
from app.config import settings
from app.core.password import verify_password
from app.core.jwt import create_access_token
from app.schemas.auth import LoginRequest
from app.core.refresh_token import generate_refresh_token
from app.core.refresh_token import validate_refresh_token
from app.core.jwt import create_access_token
from uuid import UUID
from app.core.refresh_token import revoke_refresh_token

class DuplicateEmailError(Exception):
    pass
class InvalidCredentialsError(Exception):
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

def login_user(user_data: LoginRequest) -> dict:
    with psycopg.connect(settings.database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, email, password_hash
                FROM users
                WHERE email = %s;
                """,
                (str(user_data.email),)
            )

            user = cursor.fetchone()

    if user is None:
        raise InvalidCredentialsError("Invalid email or password")

    user_id, name, email, password_hash = user

    if not verify_password(user_data.password, password_hash):
        raise InvalidCredentialsError("Invalid email or password")

    access_token = create_access_token(user_id)
    refresh_token = generate_refresh_token(str(user_id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(user_id),
            "name": name,
            "email": email
        }
    }

def refresh_access_token(refresh_token: str) -> dict:
    user_id = validate_refresh_token(refresh_token)

    if user_id is None:
        raise InvalidCredentialsError("Invalid or expired refresh token")

    return {
        "access_token": create_access_token(UUID(user_id)),
        "token_type": "bearer"
    }

def logout_user(refresh_token: str) -> bool:
    return revoke_refresh_token(refresh_token)