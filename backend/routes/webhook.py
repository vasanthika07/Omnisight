from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uuid
import time
from backend.agents.orchestrator import AgenticOrchestrator

router = APIRouter(prefix="/webhook", tags=["CI/CD Integration"])
orchestrator = AgenticOrchestrator(headless=True)

class CIWebhookPayload(BaseModel):
    repository: str = Field(default="infotact/omnisight-store")
    commit_sha: str = Field(default="a7d83ef")
    branch: str = Field(default="staging")
    environment: str = Field(default="staging")
    staging_url: Optional[str] = None
    author: Optional[str] = "frontend-dev@infotact.com"

# In-memory webhook jobs dictionary
active_jobs: Dict[str, Any] = {}

def execute_background_ci_audit(job_id: str, staging_url: Optional[str]):
    try:
        active_jobs[job_id]["status"] = "running"
        res = orchestrator.run_self_healing_cycle(
            target_url=staging_url,
            viewport_key="mobile"
        )
        active_jobs[job_id]["status"] = "completed"
        active_jobs[job_id]["result"] = res
    except Exception as e:
        active_jobs[job_id]["status"] = "failed"
        active_jobs[job_id]["error"] = str(e)

@router.post("/build")
def receive_ci_build_webhook(payload: CIWebhookPayload, background_tasks: BackgroundTasks):
    """
    Simulates CI/CD Gateway: Intercepts build notifications from GitHub Actions / Jenkins,
    and initiates an autonomous OmniSight visual audit on the staging environment.
    """
    job_id = f"job_ci_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    active_jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "created_at": time.time(),
        "payload": payload.model_dump()
    }
    
    background_tasks.add_task(execute_background_ci_audit, job_id, payload.staging_url)
    
    return {
        "accepted": True,
        "job_id": job_id,
        "message": f"CI/CD build intercepted for {payload.repository} ({payload.branch}). OmniSight autonomous QA agent dispatched.",
        "status_url": f"/webhook/jobs/{job_id}"
    }

@router.get("/jobs/{job_id}")
def get_ci_job_status(job_id: str):
    """
    Returns the execution status of an asynchronous CI/CD webhook job.
    """
    if job_id not in active_jobs:
        return {"status": "not_found", "job_id": job_id}
    return active_jobs[job_id]
