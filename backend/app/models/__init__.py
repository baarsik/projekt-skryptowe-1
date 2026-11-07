"""Exposes all database models and common utilities to Base.metadata."""
from __future__ import annotations

from datetime import UTC, datetime

from app.core.database import Base
from app.models.expense import Category, Expense, ExpenseSplit
from app.models.group import Group, GroupMember
from app.models.settlement import Settlement
from app.models.user import PasswordResetToken, RevokedToken, User


def utc_now() -> datetime:
    return datetime.now(UTC)


def ensure_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


__all__ = [
    "Base",
    "Category",
    "Expense",
    "ExpenseSplit",
    "Group",
    "GroupMember",
    "PasswordResetToken",
    "RevokedToken",
    "Settlement",
    "User",
    "ensure_utc",
    "utc_now",
]