import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from app.main import app
from app.database import get_db
from app.core.auth import get_current_user_id
from app.database import Base
from app.models import User

# --- 1. Database Setup for Testing ---

# Use an in-memory SQLite database for fast, isolated testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" 

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """Sets up and tears down the database tables for the entire test session."""
    # Create all tables before tests run
    Base.metadata.create_all(bind=test_engine)
    yield
    # Drop all tables after tests finish
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def test_db_session():
    """
    Provides a clean, independent database session for each test function.
    Rolls back transaction after test completion to ensure isolation.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Override the app's get_db dependency to use the testing session
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    
    yield session

    # Rollback and close everything
    session.close()
    transaction.rollback()
    connection.close()


# --- 2. Authentication Fixtures ---

TEST_USER_ID = "test-user-f81d4"
TEST_AUTH_TOKEN = "Bearer TEST_AUTH_TOKEN"

@pytest.fixture(scope="function")
def authenticated_user_id():
    """Fixture to ensure a constant user ID is used for authenticated requests."""
    return TEST_USER_ID

@pytest.fixture(scope="function")
def create_test_user(test_db_session):
    """Ensure a user exists in the test DB before project creation."""
    user = User(user_id=TEST_USER_ID, email="test@vlab.com", hashed_password="hashed")
    test_db_session.add(user)
    test_db_session.commit()
    return user


# --- 3. Test Client Fixture ---

@pytest.fixture(scope="function")
def client(test_db_session, authenticated_user_id, create_test_user):
    """
    Returns an authenticated TestClient with overridden dependencies for testing.
    This ensures every test runs as the TEST_USER_ID against a clean database.
    """
    
    # Override the app's auth dependency to skip token validation and return the fixed ID
    def override_get_current_user_id():
        return authenticated_user_id

    # Apply the auth override
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id
    
    # Create the TestClient
    with TestClient(app) as client:
        yield client
    
    # Clean up overrides after testing is done
    # Note: test_db_session fixture handles cleaning up the DB session override.
    app.dependency_overrides.pop(get_current_user_id)