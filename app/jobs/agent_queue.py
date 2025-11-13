# app/jobs/agent_queue.py

from typing import Dict, Any, Optional

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
        # print(f"JOB_QUEUE: Publishing to {self.queue_name}: {job_payload}")
        # In a real setup, this would be: await sqs_client.send_message(job_payload)
        
        # For local testing, we just log and return success.
        return True