# app/dependencies.py

from sqlalchemy.orm import Session
from fastapi import Depends

# Import the foundational pieces
from app.database import get_db # Your existing database session dependency
from app.db.project_repository import ProjectRepository 
from app.jobs.agent_queue import AgentQueueService
from app.services.project_service import ProjectService
from app.services.project_service import FileStorageService # For the service injection


# --- 1. Repository Dependency ---

def get_project_repository(db: Session = Depends(get_db)) -> ProjectRepository:
    """
    Dependency function that instantiates the ProjectRepository,
    injecting the request-scoped DB session.
    """
    return ProjectRepository(db_session=db)

# --- 2. Queue Dependency ---

def get_agent_queue_service() -> AgentQueueService:
    """
    Dependency for the Agent Queue client (Singleton pattern typically used here).
    """
    # Initialize once. Using a specific queue name for this service.
    return AgentQueueService(queue_name="pi_agent_tasks")

# --- 3. Storage Dependency (Local Dev) ---

def get_file_storage_service() -> FileStorageService:
    """
    Dependency for the File Storage (S3/GCS or local).
    """
    # Base path is typically configurable via environment variable
    return FileStorageService(base_path="storage/projects")

# --- 4. Project Service Dependency (The orchestrator) ---

def get_project_service(
    repository: ProjectRepository = Depends(get_project_repository),
    storage: FileStorageService = Depends(get_file_storage_service),
    queue: AgentQueueService = Depends(get_agent_queue_service)
) -> ProjectService:
    """
    The main dependency that orchestrates the core business logic.
    It injects all necessary lower-level services/repositories.
    """
    return ProjectService(
        repository=repository,
        storage_service=storage,
        agent_queue=queue
    )