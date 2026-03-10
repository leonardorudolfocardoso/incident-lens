import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

os.environ.setdefault("DATABASE_URL", "sqlite://")
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from incident_lens.database import Base, get_db
from incident_lens.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    return TestClient(app)
