"""SQL Server integration tests; opt in with DB_INTEGRATION_TESTS=1."""

import os
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("DB_INTEGRATION_TESTS") != "1",
    reason="Start local SQL Server and set DB_INTEGRATION_TESTS=1",
)


@pytest.fixture
def database():
    from db.bootstrap import bootstrap
    from db.config import load_settings

    settings = replace(
        load_settings(), environment="test", database=f"rachunki_test_{uuid4().hex}",
    )
    bootstrap(settings)
    yield settings
    engine = settings.engine(migration=True, database="master")
    try:
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            connection.exec_driver_sql(
                f"ALTER DATABASE [{settings.database}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE"
            )
            connection.exec_driver_sql(f"DROP DATABASE [{settings.database}]")
    finally:
        engine.dispose()


def migrate(settings):
    from alembic import command
    from alembic.config import Config

    configuration = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    configuration.attributes["settings"] = settings
    command.upgrade(configuration, "head")


def test_initial_migration_is_repeatable_and_matches_models(database):
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext
    from sqlalchemy import inspect

    from db.schema import metadata

    migrate(database)
    migrate(database)
    engine = database.engine(migration=True)
    try:
        with engine.connect() as connection:
            assert set(inspect(connection).get_table_names()) == {
                "alembic_version", "users", "groups", "group_members", "categories",
                "expenses", "expense_splits", "settlements",
            }
            assert compare_metadata(MigrationContext.configure(connection), metadata) == []
    finally:
        engine.dispose()


def test_reference_seed_is_repeatable_and_preserves_edits(database):
    from sqlalchemy import text

    from db.seed import seed

    migrate(database)
    seed(database, "reference")
    engine = database.engine()
    try:
        with engine.begin() as connection:
            connection.execute(text("UPDATE categories SET name = N'Changed' WHERE id = 1"))
        seed(database, "reference")
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT COUNT(*) FROM categories")) == 3
            assert connection.scalar(text("SELECT name FROM categories WHERE id = 1")) == "Changed"
            assert connection.scalar(text("SELECT COUNT(*) FROM users")) == 0
    finally:
        engine.dispose()


def test_demo_seed_is_repeatable_and_split_amounts_add_up(database):
    from sqlalchemy import text

    from db.seed import seed

    migrate(database)
    seed(database, "demo")
    seed(database, "demo")
    engine = database.engine()
    try:
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT COUNT(*) FROM users")) == 3
            assert connection.scalar(text("SELECT COUNT(*) FROM group_members")) == 3
            assert connection.scalar(text("SELECT COUNT(*) FROM expenses")) == 1
            assert connection.scalar(text("SELECT total_amount FROM expenses")) == Decimal("10.01")
            assert connection.scalar(text("SELECT SUM(amount_owed) FROM expense_splits")) == Decimal("10.01")
            assert connection.scalar(text("SELECT COUNT(*) FROM settlements")) == 1
    finally:
        engine.dispose()


def test_seed_failure_rolls_back_all_insertions(database):
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    from db.seed import seed

    migrate(database)
    engine = database.engine(migration=True)
    try:
        with engine.begin() as connection:
            connection.execute(text("INSERT INTO categories (id, name) VALUES (99, N'Inne')"))
        with pytest.raises(IntegrityError):
            seed(database, "reference")
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT COUNT(*) FROM categories")) == 1
    finally:
        engine.dispose()


def test_unmigrated_database_cannot_be_seeded(database):
    from db.seed import seed

    with pytest.raises(ValueError, match="migrat"):
        seed(database, "reference")


def test_application_login_cannot_change_schema(database):
    from sqlalchemy.exc import DBAPIError

    engine = database.engine()
    try:
        with pytest.raises(DBAPIError), engine.begin() as connection:
            connection.exec_driver_sql("CREATE TABLE unauthorized_table (id int)")
    finally:
        engine.dispose()


def test_bootstrap_preserves_existing_data(database):
    from sqlalchemy import text

    from db.bootstrap import bootstrap
    from db.seed import seed

    migrate(database)
    seed(database, "demo")
    bootstrap(database)
    engine = database.engine()
    try:
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT COUNT(*) FROM users")) == 3
    finally:
        engine.dispose()


def test_database_rejects_invalid_money_and_duplicate_membership(database):
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    from db.seed import seed

    migrate(database)
    seed(database, "demo")
    engine = database.engine()
    try:
        for statement in (
            "UPDATE expenses SET total_amount = -1",
            "UPDATE settlements SET amount = 0",
            "UPDATE settlements SET receiver_id = sender_id",
            "INSERT INTO group_members SELECT TOP 1 * FROM group_members",
            "DELETE FROM users WHERE username = 'demo-alex'",
        ):
            with pytest.raises(IntegrityError), engine.begin() as connection:
                connection.execute(text(statement))
    finally:
        engine.dispose()


def test_grants_script_stops_before_any_mutations_in_wrong_database(database):
    import re

    from sqlalchemy import text
    from sqlalchemy.exc import DBAPIError

    script = (Path(__file__).parents[2] / "infra/sql/grant-database-access.sql").read_text()
    engine = database.engine(migration=True)
    try:
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            for name in ("id-projekt-skryptowe-1-migrate", "projekt-skryptowe-1-api-baarsik"):
                connection.exec_driver_sql(f"CREATE USER [{name}] WITHOUT LOGIN")
            # SQL clients can continue after a failed GO-delimited batch.
            for batch in re.split(r"(?im)^GO\s*$", script):
                if batch.strip():
                    try:
                        connection.exec_driver_sql(batch)
                    except DBAPIError:
                        pass
            assert connection.scalar(text("""
                SELECT COUNT(*) FROM sys.database_permissions
                WHERE grantee_principal_id = USER_ID(N'id-projekt-skryptowe-1-migrate')
                    AND permission_name = 'ALTER'
            """)) == 0
    finally:
        engine.dispose()


def test_offline_creation_script_matches_live_models(database):
    import re

    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext

    from db.schema import metadata

    script = (Path(__file__).parents[2] / "docs/schema.sql").read_text()
    engine = database.engine(migration=True)
    try:
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            for batch in re.split(r"(?im)^GO\s*$", script):
                if batch.strip():
                    connection.exec_driver_sql(batch)
            assert compare_metadata(MigrationContext.configure(connection), metadata) == []
    finally:
        engine.dispose()
