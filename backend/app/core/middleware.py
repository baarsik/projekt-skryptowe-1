from __future__ import annotations

import uuid
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import COOKIE_NAME
from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.user import RevokedToken, User

GUEST_ONLY_PATHS = {
    "/auth/signup",
    "/auth/register",
    "/auth/signin",
    "/auth/login",
    "/auth/reset-password",
    "/auth/reset-password/request",
    "/auth/reset-password/confirm",
    "/auth/forgot-password",
}

PUBLIC_PATHS = {
    "/auth/logout",
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Any:
        # Allow CORS preflight requests through
        if request.method == "OPTIONS":
            return await call_next(request)

        # 1. Extract token from cookie (primary) or Bearer header (fallback)
        token = request.cookies.get(COOKIE_NAME)
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:].strip()

        authenticated_user_id: uuid.UUID | None = None
        token_payload: dict[str, Any] | None = None

        if token:
            payload = decode_access_token(token)
            if payload and "sub" in payload and "jti" in payload:
                db = SessionLocal()
                try:
                    # Check token revocation
                    is_revoked = db.scalar(
                        select(RevokedToken.id).where(RevokedToken.jti == payload["jti"])
                    )
                    if not is_revoked:
                        try:
                            user_uuid = uuid.UUID(payload["sub"])
                            user_exists = db.scalar(
                                select(User.id).where(User.id == user_uuid)
                            )
                            if user_exists:
                                authenticated_user_id = user_uuid
                                token_payload = payload
                        except (ValueError, TypeError):
                            pass
                finally:
                    db.close()

        request.state.user_id = authenticated_user_id
        request.state.token_payload = token_payload

        normalized_path = request.url.path.rstrip("/") or "/"

        # 2. Rejection for logged-in users accessing guest-only routes
        if normalized_path in GUEST_ONLY_PATHS:
            if authenticated_user_id is not None:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Already authenticated"},
                )
            return await call_next(request)

        # 3. Public paths accessible to both authenticated and unauthenticated callers
        if normalized_path in PUBLIC_PATHS:
            return await call_next(request)

        # 4. All other existing and future endpoints require a valid token
        if authenticated_user_id is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"},
            )

        return await call_next(request)