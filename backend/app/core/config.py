from __future__ import annotations

import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# JWT configuration
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "dev-secret-key-replace-in-production-minimum-32-bytes-long"
)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# Cookie configuration
COOKIE_NAME = os.getenv("COOKIE_NAME", "access_token")
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
COOKIE_SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")
COOKIE_HTTPONLY = os.getenv("COOKIE_HTTPONLY", "true").lower() == "true"

# Password reset configuration
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = int(
    os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_HOURS", "1")
)