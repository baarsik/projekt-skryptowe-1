from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.user import User


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    expenses: Mapped[list[Expense]] = relationship(
        "Expense", back_populates="category"
    )


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    group_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("groups.id"), nullable=False
    )
    payer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=False
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    split_method: Mapped[str] = mapped_column(String(50), nullable=False)
    occurred_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.UTC if hasattr(datetime, "UTC") else None),
        nullable=False,
    )

    group: Mapped[Group] = relationship("Group", back_populates="expenses")
    payer: Mapped[User] = relationship(
        "User", back_populates="expenses", foreign_keys=[payer_id]
    )
    category: Mapped[Category] = relationship("Category", back_populates="expenses")
    splits: Mapped[list[ExpenseSplit]] = relationship(
        "ExpenseSplit", back_populates="expense", cascade="all, delete-orphan"
    )


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    expense_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("expenses.id"), nullable=False
    )
    debtor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    amount_owed: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    expense: Mapped[Expense] = relationship("Expense", back_populates="splits")
    debtor: Mapped[User] = relationship(
        "User", back_populates="splits", foreign_keys=[debtor_id]
    )