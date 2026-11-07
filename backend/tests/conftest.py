from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, init_db
from app.main import app
from app.services.email import email_service


@pytest.fixture(autouse=True)
def clean_db_and_client():
    init_db()
    email_service.clear()
    client = TestClient(app)
    client.cookies.clear()

    db = SessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()

    yield

    client.cookies.clear()