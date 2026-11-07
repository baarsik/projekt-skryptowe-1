"""Shared connection settings for local tools and Azure migrations."""

import os
import re
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.exc import DBAPIError
from sqlalchemy.pool import NullPool


@dataclass(frozen=True)
class Settings:
    environment: str
    host: str
    database: str
    port: int
    user: str
    password: str = field(repr=False)
    admin_password: str = field(repr=False)
    authentication: str

    @classmethod
    def from_environment(cls, environment: Mapping[str, str]):
        mode = environment.get("APP_ENV", "local")
        if mode not in {"local", "test", "azure"}:
            raise ValueError("APP_ENV must be local, test or azure")
        host = environment.get("DB_HOST", "")
        database = environment.get("DB_NAME", "")
        authentication = environment.get("DB_AUTHENTICATION", "")
        if not host or not database:
            raise ValueError("DB_HOST and DB_NAME are required")
        if mode == "azure" and authentication not in {
            "ActiveDirectoryDefault", "ActiveDirectoryMSI",
        }:
            raise ValueError("Azure requires an explicit supported DB_AUTHENTICATION")
        port = int(environment.get("DB_PORT", environment.get("LOCAL_SQL_PORT", "1433")))
        if not 1 <= port <= 65535:
            raise ValueError("Database port must be between 1 and 65535")
        return cls(
            mode, host, database, port, environment.get("DB_USER", "rachunki_app"),
            environment.get("LOCAL_SQL_APP_PASSWORD", ""),
            environment.get("LOCAL_SQL_ADMIN_PASSWORD", ""), authentication,
        )

    def require_local(self):
        if (
            self.environment not in {"local", "test"}
            or self.host not in {"127.0.0.1", "localhost", "db"}
            or not re.fullmatch(r"rachunki_(?:dev|test)(?:_[a-zA-Z0-9]+)*", self.database)
        ):
            raise ValueError("Local operations require a local rachunki_dev/test database")
        if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_]{0,63}", self.user) or self.user.casefold() == "sa":
            raise ValueError("Use a separate local application login")

    def url(self, *, migration=False, database=None):
        local = self.environment in {"local", "test"}
        query = {"Encrypt": "yes", "TrustServerCertificate": "yes" if local else "no"}
        username, password = "", None
        if local:
            self.require_local()
            username = "sa" if migration else self.user
            password = self.admin_password if migration else self.password
            if not password:
                raise ValueError("Set the required local SQL password in .env")
        else:
            query["authentication"] = self.authentication
        return URL.create(
            "mssql+mssqlpython", username=username, password=password,
            host=self.host, port=self.port, database=database or self.database, query=query,
        )

    def engine(self, *, migration=False, database=None):
        return create_engine(
            self.url(migration=migration, database=database),
            poolclass=NullPool, hide_parameters=True, connect_args={"timeout": 10},
        )


def load_settings():
    # CI/Azure use only process settings; a local file must never override them.
    if not os.environ.get("CI") and os.environ.get("APP_ENV") != "azure":
        load_dotenv(Path(__file__).resolve().parents[2] / ".env", override=False)
    return Settings.from_environment(os.environ)


def connect(engine, *, attempts=12, delay=5):
    """Retry connection establishment (SQL startup/auto-resume), never writes."""
    for attempt in range(attempts):
        try:
            return engine.connect()
        except DBAPIError:
            if attempt == attempts - 1:
                raise
            time.sleep(delay)
