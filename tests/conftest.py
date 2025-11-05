import os
os.environ.setdefault("SHELVIA_DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("API_KEY", "supersecretkey")

import pytest
from fastapi.testclient import TestClient

from main import app
from db import create_db_and_tables

create_db_and_tables()

@pytest.fixture(scope="session")
def client():
    return TestClient(app)
