"""Current SQLAlchemy schema; historical migrations keep their own definitions."""

import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.mssql import DATETIME2

metadata = sa.MetaData(naming_convention={
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
})


def identifier():
    return sa.Column("id", sa.Uuid(), primary_key=True, default=uuid.uuid4)


def timestamp(name):
    return sa.Column(name, DATETIME2(), nullable=False, server_default=sa.text("SYSUTCDATETIME()"))


users = sa.Table(
    "users", metadata, identifier(),
    sa.Column("name", sa.Unicode(100), nullable=False),
    sa.Column("username", sa.Unicode(100), nullable=False, unique=True),
    sa.Column("email", sa.Unicode(254), nullable=False, unique=True),
    sa.Column("password_hash", sa.String(255), nullable=False), timestamp("created_at"),
)
groups = sa.Table(
    "groups", metadata, identifier(),
    sa.Column("name", sa.Unicode(100), nullable=False), timestamp("created_at"),
)
group_members = sa.Table(
    "group_members", metadata,
    sa.Column("group_id", sa.Uuid(), sa.ForeignKey("groups.id"), primary_key=True),
    sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id"), primary_key=True),
    timestamp("joined_at"),
)
categories = sa.Table(
    "categories", metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=False),
    sa.Column("name", sa.Unicode(100), nullable=False, unique=True),
)
expenses = sa.Table(
    "expenses", metadata, identifier(),
    sa.Column("group_id", sa.Uuid(), sa.ForeignKey("groups.id"), nullable=False),
    sa.Column("payer_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id"), nullable=False),
    sa.Column("description", sa.Unicode(500), nullable=False),
    sa.Column("total_amount", sa.Numeric(19, 2), nullable=False),
    sa.Column("split_method", sa.String(20), nullable=False),
    sa.Column("occurred_on", sa.DATE, nullable=False), timestamp("created_at"),
    sa.CheckConstraint("total_amount > 0", name="positive_total"),
)
expense_splits = sa.Table(
    "expense_splits", metadata, identifier(),
    sa.Column("expense_id", sa.Uuid(), sa.ForeignKey("expenses.id"), nullable=False),
    sa.Column("debtor_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("amount_owed", sa.Numeric(19, 2), nullable=False),
    sa.UniqueConstraint("expense_id", "debtor_id"),
    sa.CheckConstraint("amount_owed >= 0", name="nonnegative_share"),
)
settlements = sa.Table(
    "settlements", metadata, identifier(),
    sa.Column("group_id", sa.Uuid(), sa.ForeignKey("groups.id"), nullable=False),
    sa.Column("sender_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("receiver_id", sa.Uuid(), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("amount", sa.Numeric(19, 2), nullable=False),
    sa.Column("status", sa.Integer, nullable=False),
    sa.Column("occurred_on", sa.DATE, nullable=False),
    timestamp("created_at"), timestamp("updated_at"),
    sa.CheckConstraint("amount > 0", name="positive_amount"),
    sa.CheckConstraint("sender_id <> receiver_id", name="different_participants"),
)
