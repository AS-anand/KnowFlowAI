from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import LogoutRequest, RefreshRequest, RegisterRequest
from app.services.auth_service import (
    logout_user,
    refresh_access_token,
    register_user,
    DuplicateEmailError
)

from fastapi import Depends
from app.api.dependencies import get_current_user

from app.schemas.auth import LoginRequest
from app.services.auth_service import (
    login_user,
    InvalidCredentialsError
)
from fastapi import Depends
from app.api.dependencies import get_current_user

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


@router.get("/test-auth")
def test_auth(current_user: dict = Depends(get_current_user)):
    return {
        "message": "Authentication successful",
        "user": current_user
    }

@router.post("/login")
def login(request: LoginRequest):
    try:
        return login_user(request)

    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

@router.post("/refresh")
def refresh(request: RefreshRequest):
    try:
        return refresh_access_token(request.refresh_token)

    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

@router.post("/logout")
def logout(request: LogoutRequest):
    logout_user(request.refresh_token)

    return {"message": "Logged out successfully"}

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user