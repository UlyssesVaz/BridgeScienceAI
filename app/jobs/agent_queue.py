# app/jobs/agent_queue.py

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import json 
import time

# NOTE: This uses synchronous 'fire-and-forget' for simplicity
# In production, this would use a real async library like aiobotocore (SQS) or aio-pika (RabbitMQ)

class AgentQueueService:
    """
    Service to abstract the job queue mechanism (e.g., SQS, Redis/Celery).
    FastAPI calls this to delegate work.
    """
    def __init__(self, queue_name: str = "agent_tasks"):
        self.queue_name = queue_name

    async def enqueue_agent_task(
        self, 
        project_id: str, 
        agent_name: str, 
        task_data: Dict[str, Any]
    ) -> bool:
        """
        Pushes a task payload to the queue. Returns True if successfully queued.
        """
        job_payload = {
            "project_id": project_id,
            "agent": agent_name,
            "data": task_data,
            "queued_at": datetime.now(timezone.utc).isoformat() 
        }
        
        # --- SCALABLE BOILERPLATE ---
        # NOTE: If we were using a real client, the serialization to string 
        # is necessary here because the queue system (e.g., SQS) expects a string payload.
        
        print(f"DEBUG: Job Queued (ID: {project_id}) to {self.queue_name}")
        time.sleep(0.01) # Small delay to simulate network latency if testing synchronously
        
        # For local testing, we just return success.
        return True