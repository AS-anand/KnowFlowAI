from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2id."""
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its stored Argon2 hash."""
    try:
        return password_hasher.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False