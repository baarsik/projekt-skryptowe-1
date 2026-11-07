"""Create an isolated local database and its limited application login."""

from sqlalchemy import text

from db.config import connect, load_settings


def bootstrap(settings):
    settings.require_local()
    if not settings.password:
        raise ValueError("LOCAL_SQL_APP_PASSWORD is required")
    engine = settings.engine(migration=True, database="master")
    try:
        with connect(engine).execution_options(isolation_level="AUTOCOMMIT") as connection:
            if connection.scalar(text("SELECT DB_ID(:name)"), {"name": settings.database}) is None:
                connection.exec_driver_sql(f"CREATE DATABASE [{settings.database}]")
            # SQL Server DDL requires password literals. Build and quote the statement
            # inside SQL, with bound inputs; never interpolate credentials in Python.
            connection.execute(text("""
                DECLARE @sql nvarchar(max);
                IF SUSER_ID(:name) IS NULL
                    SET @sql = N'CREATE LOGIN ' + QUOTENAME(:name)
                        + N' WITH PASSWORD = ' + QUOTENAME(:password, '''');
                ELSE
                    SET @sql = N'ALTER LOGIN ' + QUOTENAME(:name)
                        + N' WITH PASSWORD = ' + QUOTENAME(:password, '''');
                EXEC sp_executesql @sql;
            """), {"name": settings.user, "password": settings.password})
    finally:
        engine.dispose()
    engine = settings.engine(migration=True)
    try:
        with connect(engine) as connection, connection.begin():
            if connection.scalar(text("SELECT USER_ID(:name)"), {"name": settings.user}) is None:
                connection.exec_driver_sql(f"CREATE USER [{settings.user}] FOR LOGIN [{settings.user}]")
            connection.exec_driver_sql(
                f"GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO [{settings.user}]"
            )
    finally:
        engine.dispose()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", action="store_true", required=True)
    parser.parse_args()
    bootstrap(load_settings())
    print("Local database and application login are ready.")
