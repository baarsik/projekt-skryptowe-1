from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.group import Group
    from app.models.user import User


class Settlement(Base):
    __tablename__ = "settlements"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    group_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("groups.id"), nullable=False
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    receiver_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    occurred_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.UTC if hasattr(datetime, "UTC") else None),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(datetime.UTC if hasattr(datetime, "UTC") else None),
        onupdate=lambda: datetime.now(datetime.UTC if hasattr(datetime, "UTC") else None),
        nullable=False,
    )

    group: Mapped[Group] = relationship("Group", back_populates="settlements")
    sender: Mapped[User] = relationship(
        "User", back_populates="sent_settlements", foreign_keys=[sender_id]
    )
    receiver: Mapped[User] = relationship(
        "User", back_populates="received_settlements", foreign_keys=[receiver_id]
    )