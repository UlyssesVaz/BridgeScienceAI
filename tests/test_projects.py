import pytest
from starlette.testclient import TestClient
from fastapi import status
from sqlalchemy.orm import Session
import io
import uuid

# Import the models to verify DB state
from app.models import Project, ProjectFile  # <-- Correct
from app.schemas.project import VirtualLabState  # FIXED: Importing the unified schema name
from .conftest import TEST_AUTH_TOKEN # Import the constant token for 401 test

# Note: The 'client', 'test_db_session', and 'authenticated_user_id' fixtures 
# are automatically available via conftest.py.

API_ENDPOINT = "/api/v1/projects"
MOCK_GOAL = "Develop a high-performance recommendation system for microservices."
MOCK_FILE_CONTENT = b"This is the abstract for the context document."

# ----------------------------------------------------
# 1. Success Tests (Happy Paths)
# ----------------------------------------------------

def test_initiate_project_success_no_file(client: TestClient, test_db_session: Session, authenticated_user_id: str):
    """
    Test successful project creation with only the required 'research_goal'.
    Verifies API response structure and DB persistence.
    """
    # Act
    response = client.post(
        API_ENDPOINT,
        data={"research_goal": MOCK_GOAL},
        headers={"Authorization": TEST_AUTH_TOKEN} # Auth header is optional here due to override, but good practice
    )

    # --- DEBUGGING LOG ADDED ---
    if response.status_code != status.HTTP_200_OK:
        print("\n[DEBUG LOG] test_initiate_project_success_no_file FAILED.")
        print(f"Expected 200, got {response.status_code}. Response Content (Traceback likely):")
        print(response.text)
        print("---------------------------\n")
    # ---------------------------

    # Assert API Response
    assert response.status_code == status.HTTP_200_OK
    response_data: VirtualLabState = response.json()
    
    # Check key fields in the response schema
    # FIXED: The response now uses the key "research_goal" for the user's input.
    assert response_data["research_goal"] == MOCK_GOAL 
    assert response_data["next_agent"] == "user_approval"
    assert len(response_data["task_list"]) == 1
    assert len(response_data["audit_log"]) == 1

    # Check DB Persistence
    # Query Project table
    db_project: Project = test_db_session.query(Project).filter_by(owner_id=authenticated_user_id).first()
    assert db_project is not None
    assert db_project.original_research_goal == MOCK_GOAL
    assert db_project.owner_id == authenticated_user_id
    
    # Check ProjectFile table (should be empty for this test)
    db_files = test_db_session.query(ProjectFile).filter_by(project_id=db_project.project_id).all()
    assert len(db_files) == 0


def test_initiate_project_success_with_file(client: TestClient, test_db_session: Session, authenticated_user_id: str):
    """
    Test successful project creation including an optional context file upload.
    Verifies file metadata is correctly captured in the DB.
    """
    # Arrange
    filename = "context_paper.pdf"
    
    # FastAPI's TestClient requires files to be passed as a tuple: (filename, content, media_type)
    files = {"context_docs": (filename, MOCK_FILE_CONTENT, "application/pdf")}
    
    # Act
    response = client.post(
        API_ENDPOINT,
        data={"research_goal": "Analyze the attached context paper."},
        files=files
    )

    # --- DEBUGGING LOG ADDED ---
    if response.status_code != status.HTTP_200_OK:
        print("\n[DEBUG LOG] test_initiate_project_success_with_file FAILED.")
        print(f"Expected 200, got {response.status_code}. Response Content (Traceback likely):")
        print(response.text)
        print("---------------------------\n")
    # ---------------------------

    # Assert API Response
    assert response.status_code == status.HTTP_200_OK
    
    # Assert DB Persistence
    db_project: Project = test_db_session.query(Project).filter_by(owner_id=authenticated_user_id).first()
    assert db_project is not None
    
    # Check ProjectFile table (must contain one entry)
    db_file: ProjectFile = test_db_session.query(ProjectFile).filter_by(project_id=db_project.project_id).first()
    
    assert db_file is not None
    assert db_file.filename == filename
    assert db_file.file_type == "application/pdf"
    # Note: context_docs.size is mocked as content length for TestClient
    assert db_file.file_size == len(MOCK_FILE_CONTENT)
    assert db_file.storage_path.startswith("/path/to/storage/") # Verify the mock path creation


# ----------------------------------------------------
# 2. Failure Tests
# ----------------------------------------------------

def test_initiate_project_missing_goal_400(client: TestClient):
    """
    Test API response when the required 'research_goal' form field is missing or empty.
    """
    # Test case 1: Goal field is completely missing from form data
    response_missing = client.post(API_ENDPOINT, data={})
    # This should be 422
    assert response_missing.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test case 2: Goal field is explicitly empty string (handled by application logic in main.py)
    response_empty = client.post(API_ENDPOINT, data={"research_goal": ""})
    assert response_empty.status_code == status.HTTP_400_BAD_REQUEST
    # FIX: Assertion updated to match the actual returned message from your log: "research_goal cannot be empty"
    assert "research_goal cannot be empty" in response_empty.json()["detail"]


def test_initiate_project_unauthorized_401():
    """
    Test API response when authentication fails (token is invalid or missing).
    This test *must* use a separate, un-overridden TestClient to trigger the real auth dependency.
    """
    from app.main import app as main_app
    
    # Create a client *without* dependency overrides
    unauth_client = TestClient(main_app)
    
    # Case 1: Missing Authorization Header
    response_missing = unauth_client.post(API_ENDPOINT, data={"research_goal": MOCK_GOAL})
    # NOTE: Your failure was asserting 403 == 401. This assertion keeps 401 as expected.
    assert response_missing.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_missing.json()["detail"] == "Invalid authentication credentials"

    # Case 2: Invalid Authorization Header (anything not 'Bearer TEST_AUTH_TOKEN' in the mock)
    response_invalid = unauth_client.post(
        API_ENDPOINT, 
        data={"research_goal": MOCK_GOAL}, 
        headers={"Authorization": "Bearer WRONG_TOKEN"}
    )
    assert response_invalid.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_invalid.json()["detail"] == "Invalid authentication credentials"