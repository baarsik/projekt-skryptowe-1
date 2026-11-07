from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserOut


class SignUpRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=255)
    # Capped at 72 bytes to prevent silent bcrypt truncation
    password: str = Field(..., min_length=6, max_length=72)


class SignInRequest(BaseModel):
    username: str = Field(..., min_length=1)  # Can be username or email
    password: str = Field(..., min_length=1, max_length=72)


class PasswordResetRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)


class PasswordResetConfirm(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    token: str = Field(..., min_length=1)
    password: str = Field(..., min_length=6, max_length=72, alias="new_password")


class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=72)
    new_password: str = Field(..., min_length=6, max_length=72)


class AuthResponse(BaseModel):
    message: str
    user: UserOut


class MessageResponse(BaseModel):
    message: str


class PasswordResetResponse(BaseModel):
    message: str
    reset_token: str | None = None