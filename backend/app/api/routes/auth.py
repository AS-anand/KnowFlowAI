from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import RegisterRequest
from app.services.auth_service import (
    register_user,
    DuplicateEmailError
)

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
def register(request: RegisterRequest):
    try:
        user = register_user(request)
        return {
            "message": "Registration successful",
            "user": user
        }

    except DuplicateEmailError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )