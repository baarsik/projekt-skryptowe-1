"""Connections are built from environment settings, never stored in this file."""

from alembic import context

from db.config import connect, load_settings
from db.schema import metadata

if context.is_offline_mode():
    context.configure(
        dialect_name="mssql", target_metadata=metadata,
        literal_binds=True, dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    settings = context.config.attributes.get("settings") or load_settings()
    engine = settings.engine(migration=True)
    try:
        with connect(engine) as connection:
            context.configure(connection=connection, target_metadata=metadata, compare_type=True)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()
