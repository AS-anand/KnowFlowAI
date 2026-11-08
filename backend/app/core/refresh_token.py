import hashlib
import secrets

from app.core.redis import redis_client

REFRESH_TOKEN_EXPIRE_SECONDS = 7 * 24 * 60 * 60


def generate_refresh_token(user_id: str) -> str:
    # Generate a cryptographically secure opaque token.
    refresh_token = secrets.token_urlsafe(64)

    # Store only its SHA-256 hash in Redis.
    token_hash = hashlib.sha256(
        refresh_token.encode("utf-8")
    ).hexdigest()

    redis_client.setex(
        f"refresh_token:{token_hash}",
        REFRESH_TOKEN_EXPIRE_SECONDS,
        user_id
    )

    # Return the raw token to the client.
    return refresh_token

def validate_refresh_token(refresh_token: str) -> str | None:
    token_hash = hashlib.sha256(
        refresh_token.encode("utf-8")
    ).hexdigest()

    user_id = redis_client.get(f"refresh_token:{token_hash}")

    return user_id

def revoke_refresh_token(refresh_token: str) -> bool:
    token_hash = hashlib.sha256(
        refresh_token.encode("utf-8")
    ).hexdigest()

    deleted = redis_client.delete(f"refresh_token:{token_hash}")

    return deleted == 1