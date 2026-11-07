from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SplitCreate(BaseModel):
    debtor_id: uuid.UUID
    amount_owed: Decimal = Field(..., gt=0, decimal_places=2)


class SplitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    debtor_id: uuid.UUID
    amount_owed: Decimal


class ExpenseCreate(BaseModel):
    group_id: uuid.UUID
    category_id: int
    description: str = Field(..., min_length=1, max_length=255)
    total_amount: Decimal = Field(..., gt=0, decimal_places=2)
    split_method: str = Field(default="equal", max_length=50)
    splits: list[SplitCreate]


class ExpenseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    group_id: uuid.UUID
    payer_id: uuid.UUID
    category_id: int
    description: str
    total_amount: Decimal
    split_method: str
    occurred_on: datetime
    created_at: datetime
    splits: list[SplitOut]