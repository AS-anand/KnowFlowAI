from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RegisterRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        min_length=2,
        max_length=100
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128
    )

class LoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128
    )

class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)

class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=1)

    