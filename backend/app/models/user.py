from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.expense import Expense, ExpenseSplit
    from app.models.group import GroupMember
    from app.models.settlement import Settlement


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.UTC if hasattr(datetime, "UTC") else None),
        nullable=False,
    )

    group_memberships: Mapped[list[GroupMember]] = relationship(
        "GroupMember", back_populates="user", cascade="all, delete-orphan"
    )
    expenses: Mapped[list[Expense]] = relationship(
        "Expense", back_populates="payer", foreign_keys="Expense.payer_id"
    )
    splits: Mapped[list[ExpenseSplit]] = relationship(
        "ExpenseSplit", back_populates="debtor", foreign_keys="ExpenseSplit.debtor_id"
    )
    sent_settlements: Mapped[list[Settlement]] = relationship(
        "Settlement",
        back_populates="sender",
        foreign_keys="Settlement.sender_id",
    )
    received_settlements: Mapped[list[Settlement]] = relationship(
        "Settlement",
        back_populates="receiver",
        foreign_keys="Settlement.receiver_id",
    )


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    jti: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=True
    )
    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.UTC if hasattr(datetime, "UTC") else None),
        nullable=False,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    token: Mapped[str] = mapped_column(
        String(128), unique=True, index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.UTC if hasattr(datetime, "UTC") else None),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped[User] = relationship("User")