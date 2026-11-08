from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from jwt.exceptions import InvalidTokenError

from app.config import settings


def create_access_token(user_id: UUID) -> str:
    now = datetime.now(timezone.utc)

    expires_at = now + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expires_at,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return token

def verify_access_token(token: str) -> UUID:
    """
    Validate an access token and return the authenticated user's UUID.
    Raises InvalidTokenError if validation fails.
    """

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={
            "require": ["sub", "iat", "exp"]
        }
    )

    try:
        user_id = UUID(payload["sub"])
    except (ValueError, TypeError, AttributeError):
        raise InvalidTokenError("Invalid token subject")

    return user_id