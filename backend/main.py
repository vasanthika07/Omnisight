from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.config import (
    SCREENSHOTS_DIR,
    TEST_APP_DIR,
    ROOT_DIR,
    VISION_PROVIDER,
    OPENAI_API_KEY,
    GEMINI_API_KEY
)
from backend.routes.audit import router as audit_router
from backend.routes.webhook import router as webhook_router

app = FastAPI(
    title="OmniSight: Multimodal UI Self-Healing & RPA Agent API",
    description="Bleeding-edge autonomous visual testing, multimodal anomaly detection, and closed-loop self-healing.",
    version="1.0.0"
)

# Enable CORS for frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories
app.mount("/screenshots", StaticFiles(directory=str(SCREENSHOTS_DIR)), name="screenshots")
app.mount("/test-app", StaticFiles(directory=str(TEST_APP_DIR), html=True), name="test-app")

# Include routers
app.include_router(audit_router)
app.include_router(webhook_router)

@app.get("/")
def root():
    return {
        "project": "OmniSight: Multimodal UI Self-Healing & RPA Agent",
        "status": "operational",
        "version": "1.0.0",
        "vlm_provider_configured": "openai" if OPENAI_API_KEY else ("gemini" if GEMINI_API_KEY else "autonomous_builtin"),
        "endpoints": {
            "docs": "/docs",
            "trigger_audit": "POST /api/audit",
            "audit_history": "GET /api/history",
            "single_run": "GET /api/runs/{run_id}",
            "reset_bug": "POST /api/reset-bug",
            "approve_pr": "POST /api/approve-pr",
            "ci_webhook": "POST /webhook/build",
            "ci_jobs": "GET /webhook/jobs",
            "test_store": "/test-app/index.html"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "playwright": "ready",
        "vision_engine": "active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
