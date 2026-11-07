"""Start isolated CI SQL Server with generated, masked, ephemeral passwords."""

import os
import secrets
import subprocess
from pathlib import Path

repository = Path(__file__).resolve().parents[2]
environment = os.environ.copy()
environment.update({
    "APP_ENV": "test",
    "DB_HOST": "127.0.0.1",
    "DB_NAME": "rachunki_test",
    "DB_USER": "rachunki_app",
    "LOCAL_SQL_PORT": "1433",
    "DB_INTEGRATION_TESTS": "1",
    "COMPOSE_PROJECT_NAME": f"rachunki-ci-{os.environ['GITHUB_RUN_ID']}-{os.environ['GITHUB_JOB']}",
})
for key in ("LOCAL_SQL_ADMIN_PASSWORD", "LOCAL_SQL_APP_PASSWORD"):
    environment[key] = "Aa1!" + secrets.token_hex(24)
    print(f"::add-mask::{environment[key]}", flush=True)
keys = (
    "APP_ENV", "DB_HOST", "DB_NAME", "DB_USER", "LOCAL_SQL_PORT", "DB_INTEGRATION_TESTS",
    "COMPOSE_PROJECT_NAME", "LOCAL_SQL_ADMIN_PASSWORD", "LOCAL_SQL_APP_PASSWORD",
)
with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as output:
    for key in keys:
        output.write(f"{key}={environment[key]}\n")
subprocess.run(["docker", "compose", "up", "-d", "db"], cwd=repository, env=environment, check=True)
