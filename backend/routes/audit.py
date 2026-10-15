from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from backend.agents.orchestrator import AgenticOrchestrator
from backend.agents.fix_generator import FixGenerator
from backend.github_integration.pr_manager import GitHubPRManager
from backend.storage.db import get_recent_runs, get_run_by_id, save_audit_run

router = APIRouter(prefix="/api", tags=["Audit & Self-Healing"])
orchestrator = AgenticOrchestrator(headless=True)
fixer = FixGenerator()
pr_manager = GitHubPRManager()

class AuditRequest(BaseModel):
    viewport: str = Field(default="mobile", description="Viewport: mobile, tablet, or desktop")
    target_url: Optional[str] = Field(default=None, description="Target webpage URL or local checkout page")
    max_retries: int = Field(default=2, ge=1, le=5)

class PRApprovalRequest(BaseModel):
    run_id: str
    custom_title: Optional[str] = None
    custom_notes: Optional[str] = None

@router.post("/audit")
def start_audit(req: AuditRequest):
    """
    Executes a complete OmniSight multimodal UI inspection, self-healing, and verification cycle.
    """
    try:
        result = orchestrator.run_self_healing_cycle(
            target_url=req.target_url,
            viewport_key=req.viewport,
            max_retries=req.max_retries
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Audit execution failed: {str(exc)}")

@router.get("/history")
def get_audit_history(limit: int = 20):
    """
    Returns recent audit runs with defect logs and verification status.
    """
    try:
        runs = get_recent_runs(limit=limit)
        return {"total": len(runs), "runs": runs}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/runs/{run_id}")
def get_single_run(run_id: str):
    """
    Returns full run details, bounding boxes, patch unified diff, and before/after screenshots.
    """
    run_data = get_run_by_id(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    return run_data

@router.post("/reset-bug")
def reset_to_buggy_state():
    """
    Resets the checkout page stylesheet back to intentional buggy state for repeated demo testing.
    """
    success = fixer.reset_file_to_buggy_state()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reset stylesheet")
    return {
        "status": "reset",
        "message": "Checkout stylesheet reset to buggy state (520px fixed width). Ready for next audit demo."
    }

@router.post("/approve-pr")
def approve_and_create_pr(req: PRApprovalRequest):
    """
    Approves the verified patch and generates or opens a GitHub Pull Request.
    """
    run_data = get_run_by_id(req.run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail="Run ID not found")
    
    patch = run_data.get("patch")
    if not patch:
        raise HTTPException(status_code=400, detail="No verified patch found for this run")

    title = req.custom_title or f"fix(ui): resolve responsive viewport clipping on {patch.get('target_selector', 'button')}"
    branch = f"omnisight/fix-{req.run_id}"
    body = (
        f"## 🤖 OmniSight Automated Pull Request\n\n"
        f"**Audit Run ID:** `{req.run_id}`\n"
        f"**Target Selector:** `{patch.get('target_selector')}`\n"
        f"**File Repaired:** `{patch.get('file_path')}`\n"
        f"**QA Verification:** Passed ✅\n\n"
        f"### Unified Diff:\n```diff\n{patch.get('unified_diff')}\n```\n"
    )

    pr_res = pr_manager.create_pull_request(
        branch_name=branch,
        title=title,
        body=body,
        file_path=patch.get("file_path", "test-app/checkout.css"),
        repaired_content=patch.get("repaired_css", "")
    )

    # Update DB record with PR info
    if pr_res.get("success"):
        run_data["pr_number"] = pr_res.get("pr_number")
        run_data["pr_url"] = pr_res.get("pr_url")
        save_audit_run(run_data)

    return pr_res
