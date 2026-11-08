from uuid import uuid4

import jwt
from jwt.exceptions import InvalidTokenError

from app.core.jwt import (
    create_access_token,
    verify_access_token
)
from app.config import settings


# Test 1: Valid token
user_id = uuid4()
token = create_access_token(user_id)

decoded_user_id = verify_access_token(token)

assert decoded_user_id == user_id
print("Valid token: PASSED")


# Test 2: Tampered token
tampered_token = token[:-5] + "abcde"

try:
    verify_access_token(tampered_token)
    print("Tampered token: FAILED")
except InvalidTokenError:
    print("Tampered token: PASSED")


# Test 3: Expired token
expired_token = jwt.encode(
    {
        "sub": str(user_id),
        "iat": 1000000000,
        "exp": 1000000001
    },
    settings.jwt_secret_key,
    algorithm=settings.jwt_algorithm
)

try:
    verify_access_token(expired_token)
    print("Expired token: FAILED")
except InvalidTokenError:
    print("Expired token: PASSED")