from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import (
    COOKIE_HTTPONLY,
    COOKIE_NAME,
    COOKIE_SAMESITE,
    COOKIE_SECURE,
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS,
)
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.user import PasswordResetToken, RevokedToken, User
from app.schemas.auth import (
    AuthResponse,
    MessageResponse,
    PasswordChange,
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetResponse,
    SignInRequest,
    SignUpRequest,
)
from app.schemas.user import UserOut
from app.services.email import email_service

router = APIRouter(prefix="/auth", tags=["auth"])


def utc_now() -> datetime:
    return datetime.now(UTC)


def ensure_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(
    req: SignUpRequest,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> AuthResponse:
    existing_user = db.scalar(
        select(User).where((User.username == req.username) | (User.email == req.email))
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )

    new_user = User(
        name=req.name,
        username=req.username,
        email=req.email,
        password_hash=hash_password(req.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token, _ = create_access_token(
        user_id=new_user.id,
        username=new_user.username,
        email=new_user.email,
    )

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
    )

    return AuthResponse(
        message="User registered successfully",
        user=UserOut.model_validate(new_user),
    )


@router.post("/signin", response_model=AuthResponse)
@router.post("/login", response_model=AuthResponse)
def signin(
    req: SignInRequest,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> AuthResponse:
    user = db.scalar(
        select(User).where((User.username == req.username) | (User.email == req.username))
    )
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token, _ = create_access_token(
        user_id=user.id,
        username=user.username,
        email=user.email,
    )

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
    )

    return AuthResponse(
        message="Signed in successfully",
        user=UserOut.model_validate(user),
    )


@router.post("/logout", response_model=MessageResponse)
def logout(
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()

    if token:
        payload = decode_access_token(token)
        if payload and "jti" in payload:
            jti = payload["jti"]
            existing = db.scalar(select(RevokedToken.id).where(RevokedToken.jti == jti))
            if not existing:
                exp_timestamp = payload.get("exp")
                expires_at = (
                    datetime.fromtimestamp(exp_timestamp, tz=UTC)
                    if exp_timestamp
                    else None
                )
                sub_id = payload.get("sub")
                user_uuid = None
                if sub_id:
                    try:
                        user_uuid = uuid.UUID(sub_id)
                    except ValueError:
                        pass
                revocation = RevokedToken(
                    jti=jti,
                    user_id=user_uuid,
                    expires_at=expires_at,
                )
                db.add(revocation)
                db.commit()

    response.delete_cookie(key=COOKIE_NAME, path="/")
    return MessageResponse(message="Logged out successfully")


@router.post("/reset-password/request", response_model=PasswordResetResponse)
@router.post("/forgot-password", response_model=PasswordResetResponse)
def request_password_reset(
    req: PasswordResetRequest, db: Annotated[Session, Depends(get_db)]
) -> PasswordResetResponse:
    user = db.scalar(select(User).where(User.email == req.email))
    if not user:
        return PasswordResetResponse(
            message="Password reset instructions sent if email exists"
        )

    reset_token = secrets.token_urlsafe(32)
    expires_at = utc_now() + timedelta(hours=PASSWORD_RESET_TOKEN_EXPIRE_HOURS)

    record = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at,
        used=False,
    )
    db.add(record)
    db.commit()

    email_service.send_password_reset_email(to_email=user.email, reset_token=reset_token)

    return PasswordResetResponse(
        message="Password reset instructions sent if email exists",
        reset_token=reset_token,
    )


@router.post("/reset-password", response_model=MessageResponse)
@router.post("/reset-password/confirm", response_model=MessageResponse)
def confirm_password_reset(
    req: PasswordResetConfirm, db: Annotated[Session, Depends(get_db)]
) -> MessageResponse:
    record = db.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.token == req.token,
            PasswordResetToken.used.is_(False),
        )
    )

    if not record or ensure_utc(record.expires_at) < utc_now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user = db.scalar(select(User).where(User.id == record.user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User associated with token not found",
        )

    user.password_hash = hash_password(req.password)
    record.used = True
    db.commit()

    return MessageResponse(message="Password reset successfully")


@router.post("/change-password", response_model=MessageResponse)
def change_password(
    req: PasswordChange,
    request: Request,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    user = get_current_user(request, db)

    if not verify_password(req.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    user.password_hash = hash_password(req.new_password)

    # Revoke current token
    token_payload = getattr(request.state, "token_payload", None)
    if token_payload and "jti" in token_payload:
        jti = token_payload["jti"]
        existing = db.scalar(select(RevokedToken.id).where(RevokedToken.jti == jti))
        if not existing:
            exp_timestamp = token_payload.get("exp")
            expires_at = (
                datetime.fromtimestamp(exp_timestamp, tz=UTC)
                if exp_timestamp
                else None
            )
            db.add(
                RevokedToken(
                    jti=jti,
                    user_id=user.id,
                    expires_at=expires_at,
                )
            )

    # Issue fresh token
    new_token, _ = create_access_token(
        user_id=user.id,
        username=user.username,
        email=user.email,
    )
    response.set_cookie(
        key=COOKIE_NAME,
        value=new_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path="/",
    )

    db.commit()
    return MessageResponse(message="Password changed successfully")


@router.get("/me", response_model=UserOut)
def get_me(request: Request, db: Annotated[Session, Depends(get_db)]) -> UserOut:
    user = get_current_user(request, db)
    return UserOut.model_validate(user)