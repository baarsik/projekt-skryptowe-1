"""Initial household schema from docs/schema.md (issue #15)."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mssql import DATETIME2

revision = "20261107_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.Unicode(100), nullable=False),
        sa.Column("username", sa.Unicode(100), nullable=False),
        sa.Column("email", sa.Unicode(254), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", DATETIME2(), server_default=sa.text("SYSUTCDATETIME()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_table(
        "groups",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.Unicode(100), nullable=False),
        sa.Column("created_at", DATETIME2(), server_default=sa.text("SYSUTCDATETIME()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_groups"),
    )
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("name", sa.Unicode(100), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_categories"),
        sa.UniqueConstraint("name", name="uq_categories_name"),
    )
    op.create_table(
        "group_members",
        sa.Column("group_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("joined_at", DATETIME2(), server_default=sa.text("SYSUTCDATETIME()"), nullable=False),
        sa.PrimaryKeyConstraint("group_id", "user_id", name="pk_group_members"),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], name="fk_group_members_group_id_groups"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_group_members_user_id_users"),
    )
    op.create_table(
        "expenses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("group_id", sa.Uuid(), nullable=False),
        sa.Column("payer_id", sa.Uuid(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("description", sa.Unicode(500), nullable=False),
        sa.Column("total_amount", sa.Numeric(19, 2), nullable=False),
        sa.Column("split_method", sa.String(20), nullable=False),
        sa.Column("occurred_on", sa.DATE(), nullable=False),
        sa.Column("created_at", DATETIME2(), server_default=sa.text("SYSUTCDATETIME()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_expenses"),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], name="fk_expenses_group_id_groups"),
        sa.ForeignKeyConstraint(["payer_id"], ["users.id"], name="fk_expenses_payer_id_users"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], name="fk_expenses_category_id_categories"),
        sa.CheckConstraint("total_amount > 0", name=op.f("ck_expenses_positive_total")),
    )
    op.create_table(
        "expense_splits",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("expense_id", sa.Uuid(), nullable=False),
        sa.Column("debtor_id", sa.Uuid(), nullable=False),
        sa.Column("amount_owed", sa.Numeric(19, 2), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_expense_splits"),
        sa.ForeignKeyConstraint(["expense_id"], ["expenses.id"], name="fk_expense_splits_expense_id_expenses"),
        sa.ForeignKeyConstraint(["debtor_id"], ["users.id"], name="fk_expense_splits_debtor_id_users"),
        sa.UniqueConstraint("expense_id", "debtor_id", name="uq_expense_splits_expense_id"),
        sa.CheckConstraint("amount_owed >= 0", name=op.f("ck_expense_splits_nonnegative_share")),
    )
    op.create_table(
        "settlements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("group_id", sa.Uuid(), nullable=False),
        sa.Column("sender_id", sa.Uuid(), nullable=False),
        sa.Column("receiver_id", sa.Uuid(), nullable=False),
        sa.Column("amount", sa.Numeric(19, 2), nullable=False),
        sa.Column("status", sa.Integer(), nullable=False),
        sa.Column("occurred_on", sa.DATE(), nullable=False),
        sa.Column("created_at", DATETIME2(), server_default=sa.text("SYSUTCDATETIME()"), nullable=False),
        sa.Column("updated_at", DATETIME2(), server_default=sa.text("SYSUTCDATETIME()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_settlements"),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"], name="fk_settlements_group_id_groups"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], name="fk_settlements_sender_id_users"),
        sa.ForeignKeyConstraint(["receiver_id"], ["users.id"], name="fk_settlements_receiver_id_users"),
        sa.CheckConstraint("amount > 0", name=op.f("ck_settlements_positive_amount")),
        sa.CheckConstraint("sender_id <> receiver_id", name=op.f("ck_settlements_different_participants")),
    )


def downgrade():
    for name in ("settlements", "expense_splits", "expenses", "group_members", "categories", "groups", "users"):
        op.drop_table(name)
