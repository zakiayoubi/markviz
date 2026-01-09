import pytest
from fastapi.testclient import TestClient

# TestClient simulates https requests to your fast api app
# without running a real server
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..main import app
from ..database import Base, get_db
from ..models import User


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    # SQLite normally restricts to one thread
    poolclass=StaticPool,  # Keep connection alive for in-memory DB
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture
def db():
    """
    Create a fresh database for each test.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create a new session
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """Create a test client that uses the test database."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    # Override the normal database with our test database
    app.dependency_overrides[get_db] = override_get_db

    # Create test client
    with TestClient(app) as test_client:
        yield test_client

    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client, db):
    user_data = {
        "first_name": "Zaki",
        "last_name": "Ayoubi",
        "email": "zaki@markviz.com",
        "password": "zaki1212",
    }

    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    return db.query(User).filter(User.email == user_data["email"]).first()
