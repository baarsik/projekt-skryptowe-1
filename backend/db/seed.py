"""Transactional reference data and explicit local-only demo fixtures."""

import argparse
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import and_, select

from db import schema
from db.config import load_settings


def ensure_row(connection, table, values):
    condition = and_(*(column == values[column.name] for column in table.primary_key))
    if connection.execute(select(table).where(condition)).first() is None:
        connection.execute(table.insert().values(**values))


def seed(settings, profile="reference"):
    if profile not in {"reference", "demo"}:
        raise ValueError("Seed profile must be reference or demo")
    if profile == "demo":
        settings.require_local()
    engine = settings.engine()
    try:
        with engine.begin() as connection:
            config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
            expected = ScriptDirectory.from_config(config).get_current_head()
            if MigrationContext.configure(connection).get_current_revision() != expected:
                raise ValueError("Apply all migrations before seeding")
            for identifier, name in ((1, "Jedzenie"), (2, "Transport"), (3, "Inne")):
                ensure_row(connection, schema.categories, {"id": identifier, "name": name})
            if profile == "demo":
                seed_demo(connection)
    finally:
        engine.dispose()


def seed_demo(connection):
    household = UUID("00000000-0000-4000-8000-000000000001")
    expense = UUID("00000000-0000-4000-8000-000000000002")
    users = [UUID(f"00000000-0000-4000-8000-{number:012d}") for number in (11, 12, 13)]
    ensure_row(connection, schema.groups, {"id": household, "name": "Demo household"})
    for user, name in zip(users, ("alex", "blair", "casey"), strict=True):
        ensure_row(connection, schema.users, {
            "id": user, "name": f"Demo {name.title()}", "username": f"demo-{name}",
            "email": f"demo-{name}@example.invalid", "password_hash": "!login-disabled",
        })
        ensure_row(connection, schema.group_members, {"group_id": household, "user_id": user})
    ensure_row(connection, schema.expenses, {
        "id": expense, "group_id": household, "payer_id": users[0], "category_id": 1,
        "description": "Demo shared groceries", "total_amount": Decimal("10.01"),
        "split_method": "equal", "occurred_on": date(2026, 1, 1),
    })
    for index, (debtor, amount) in enumerate(zip(users, ("3.34", "3.34", "3.33"), strict=True), 21):
        ensure_row(connection, schema.expense_splits, {
            "id": UUID(f"00000000-0000-4000-8000-{index:012d}"),
            "expense_id": expense, "debtor_id": debtor, "amount_owed": Decimal(amount),
        })
    ensure_row(connection, schema.settlements, {
        "id": UUID("00000000-0000-4000-8000-000000000003"),
        "group_id": household, "sender_id": users[1], "receiver_id": users[0],
        "amount": Decimal("1.00"), "status": 0, "occurred_on": date(2026, 1, 2),
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("reference", "demo"), default="reference")
    arguments = parser.parse_args()
    seed(load_settings(), arguments.profile)
    print(f"Applied {arguments.profile} seed data.")
