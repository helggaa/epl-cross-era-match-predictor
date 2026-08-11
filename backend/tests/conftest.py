import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app

engine = create_engine(settings.DATABASE_URL)

@pytest.fixture(scope="module")
def db_session() -> Session:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)
