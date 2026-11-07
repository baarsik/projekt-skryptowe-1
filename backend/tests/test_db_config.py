import pytest


def local_environment():
    return {
        "APP_ENV": "local",
        "DB_HOST": "127.0.0.1",
        "DB_NAME": "rachunki_dev",
        "DB_USER": "rachunki_app",
        "LOCAL_SQL_APP_PASSWORD": "test-only-value",
        "LOCAL_SQL_ADMIN_PASSWORD": "admin-test-only-value",
    }


def test_local_urls_escape_passwords_and_separate_application_permissions():
    from db.config import Settings

    environment = local_environment()
    environment["LOCAL_SQL_APP_PASSWORD"] = "a@:/%;}'secret"
    settings = Settings.from_environment(environment)
    application = settings.url()
    migration = settings.url(migration=True)
    assert application.username == "rachunki_app"
    assert application.password == "a@:/%;}'secret"
    assert migration.username == "sa"
    assert migration.password == "admin-test-only-value"
    assert application.query["TrustServerCertificate"] == "yes"
    assert "secret" not in repr(settings)
    assert "test-only-value" not in repr(settings)


@pytest.mark.parametrize("field", ["DB_HOST", "DB_NAME", "DB_AUTHENTICATION"])
def test_azure_requires_explicit_connection_settings(field):
    from db.config import Settings

    environment = {
        "APP_ENV": "azure",
        "DB_HOST": "example.database.windows.net",
        "DB_NAME": "rachunki-db",
        "DB_AUTHENTICATION": "ActiveDirectoryDefault",
    }
    del environment[field]
    with pytest.raises(ValueError):
        Settings.from_environment(environment)


def test_azure_uses_encrypted_passwordless_connection():
    from db.config import Settings

    settings = Settings.from_environment({
        "APP_ENV": "azure",
        "DB_HOST": "example.database.windows.net",
        "DB_NAME": "rachunki-db",
        "DB_AUTHENTICATION": "ActiveDirectoryDefault",
    })
    url = settings.url(migration=True)
    assert url.username == ""
    assert url.password is None
    assert url.query["authentication"] == "ActiveDirectoryDefault"
    assert url.query["Encrypt"] == "yes"
    assert url.query["TrustServerCertificate"] == "no"


@pytest.mark.parametrize("changes", [
    {"DB_HOST": "example.database.windows.net"},
    {"DB_NAME": "rachunki-db"},
    {"DB_NAME": "rachunki_dev]; DROP DATABASE master;--"},
    {"APP_ENV": "azure"},
    {"DB_USER": "SA"},
    {"DB_USER": "Sa"},
])
def test_local_operations_reject_remote_or_unsafe_targets(changes):
    from db.config import Settings

    environment = local_environment() | changes
    environment["DB_AUTHENTICATION"] = "ActiveDirectoryDefault"
    with pytest.raises(ValueError):
        Settings.from_environment(environment).require_local()


def test_local_operations_allow_isolated_ci_database():
    from db.config import Settings

    environment = local_environment() | {
        "APP_ENV": "test", "DB_HOST": "db", "DB_NAME": "rachunki_test_123",
    }
    Settings.from_environment(environment).require_local()


def test_demo_seeding_rejects_azure_before_attempting_a_connection(monkeypatch):
    from db.config import Settings
    from db.seed import seed

    settings = Settings.from_environment({
        "APP_ENV": "azure", "DB_HOST": "example.database.windows.net",
        "DB_NAME": "rachunki-db", "DB_AUTHENTICATION": "ActiveDirectoryDefault",
    })

    def forbidden_connection(*args, **kwargs):
        pytest.fail("Demo seeding attempted to connect to Azure")

    monkeypatch.setattr(Settings, "engine", forbidden_connection)
    with pytest.raises(ValueError, match="Local operations"):
        seed(settings, "demo")
