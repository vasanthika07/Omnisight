"""
OmniSight Devices & Dynamic Monitoring API Routes
Provides endpoints for any-device emulation, dynamic edge case checking,
multi-device fleet audits, and continuous real-time monitoring.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import time
import uuid

from backend.devices.registry import (
    DEVICE_PRESETS,
    DEVICE_CATEGORIES,
    get_all_devices,
    get_device_by_id,
    create_custom_device
)
from backend.devices.monitor import monitor_manager, get_navigator
from backend.agents.fix_generator import FixGenerator
from backend.agents.verification import VerificationEngine
from backend.storage.db import save_audit_run

router = APIRouter(prefix="/api", tags=["Any-Device Checking & Monitoring"])
fixer = FixGenerator()
verifier = VerificationEngine()

# Pydantic Schemas
class CustomDeviceSpec(BaseModel):
    width: int = Field(default=393, ge=180, le=5120)
    height: int = Field(default=852, ge=200, le=4320)
    dpr: float = Field(default=2.0, ge=1.0, le=4.0)
    is_mobile: bool = Field(default=True)
    has_touch: bool = Field(default=True)
    orientation: str = Field(default="portrait")
    user_agent: Optional[str] = None
    color_scheme: str = Field(default="dark")
    name: Optional[str] = None

class DeviceAuditRequest(BaseModel):
    device_id: Optional[str] = Field(default="iphone_15_pro")
    custom_device: Optional[CustomDeviceSpec] = None
    target_url: Optional[str] = None
    auto_heal: bool = Field(default=True)

class MultiDeviceAuditRequest(BaseModel):
    device_ids: List[str] = Field(default=["iphone_15_pro", "galaxy_s24_ultra", "ipad_air", "desktop_1080p"])
    target_url: Optional[str] = None

class CreateMonitorRequest(BaseModel):
    name: Optional[str] = None
    target_url: str = Field(default="http://127.0.0.1:8000/test-app/index.html")
    devices: List[str] = Field(default=["iphone_15_pro", "galaxy_s24_ultra", "desktop_1080p"])
    interval_seconds: int = Field(default=60, ge=15, le=86400)
    alert_threshold: float = Field(default=85.0, ge=50.0, le=100.0)

# Endpoints
@router.get("/devices")
def list_available_devices():
    """Returns all standard device presets and categories."""
    return {
        "categories": DEVICE_CATEGORIES,
        "total_presets": len(DEVICE_PRESETS),
        "presets": get_all_devices()
    }

@router.post("/devices/audit")
def audit_any_device(req: DeviceAuditRequest):
    """
    Executes a comprehensive dynamic edge case audit on ANY device (preset or custom).
    Optionally generates responsive CSS patch, injects into DOM, and verifies healing.
    """
    navigator = get_navigator()
    
    # Resolve device configuration
    if req.custom_device:
        device_config = create_custom_device(req.custom_device.model_dump())
    else:
        device_config = get_device_by_id(req.device_id or "iphone_15_pro")

    run_id = f"dev_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    is_external = bool(req.target_url and not str(req.target_url).startswith("file://") and "test-app" not in str(req.target_url))

    try:
        # Capture before state and execute dynamic edge-case evaluation
        capture_res = navigator.capture_device(
            device_config=device_config,
            target_url=req.target_url,
            run_id=run_id,
            suffix="_before"
        )
        
        before_screenshot = capture_res["screenshot_filename"]
        before_path = capture_res["screenshot_path"]
        defects = capture_res["defects"]
        checklist = capture_res["checklist"]
        score = capture_res["compliance_score"]
        grade = capture_res["grade"]

        patch_info = None
        after_screenshot = None
        diff_screenshot = None
        verification_passed = len(defects) == 0
        pixel_stats = {"diff_pixels": 0, "diff_percentage": 0.0}

        # Autonomous healing if defects are present
        if req.auto_heal and len(defects) > 0:
            primary_defect = defects[0]
            # Synthesize targeted CSS patch
            patch_css = fixer.generate_css_patch(primary_defect)
            diff_obj = fixer.create_unified_diff(
                run_id=run_id,
                defect=primary_defect,
                is_external=is_external,
                target_url=req.target_url
            )
            patch_info = {
                "css": patch_css,
                "repaired_css": patch_css,
                "unified_diff": diff_obj.get("unified_diff"),
                "patch_file": diff_obj.get("patch_file"),
                "target_selector": primary_defect.get("element", "button"),
                "file_path": diff_obj.get("file_path", "test-app/checkout.css") if not is_external else "responsive-patch.css"
            }

            # Verify patch on the device
            verify_res = navigator.verify_device_patch(
                device_config=device_config,
                css_patch=patch_css,
                target_url=req.target_url,
                run_id=run_id
            )
            after_screenshot = verify_res["after_filename"]
            after_path = verify_res["after_path"]
            verification_passed = verify_res["verification_passed"]

            # Visual diff heatmap
            diff_filename = f"{run_id}_{device_config.get('id')}_diff.png"
            diff_screenshot = verifier.generate_visual_diff_image(
                before_path=before_path,
                after_path=after_path,
                output_filename=diff_filename
            )
            pixel_stats = verifier.last_diff_stats

        # Build response record
        audit_record = {
            "id": run_id,
            "device": device_config,
            "target_url": req.target_url or "http://127.0.0.1:8000/test-app/index.html",
            "page_title": capture_res["dom_metrics"].get("pageTitle", "Target Page"),
            "is_external": is_external,
            "compliance_score": score,
            "grade": grade,
            "checklist": checklist,
            "defects_found": len(defects),
            "defects": defects,
            "fix_applied": req.auto_heal and len(defects) > 0,
            "verification_passed": verification_passed,
            "before_screenshot": before_screenshot,
            "after_screenshot": after_screenshot,
            "diff_screenshot": diff_screenshot,
            "pixel_diff_stats": pixel_stats,
            "patch": patch_info,
            "summary": f"Audited {device_config.get('name')}: {score}% compliance score. Found {len(defects)} edge-case defect(s)."
        }

        # Save to database for history tracking
        try:
            save_audit_run({
                "id": run_id,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": "repaired" if verification_passed and len(defects) > 0 else ("passed" if len(defects) == 0 else "action_required"),
                "viewport": f"{device_config.get('name')} ({device_config.get('width')}x{device_config.get('height')})",
                "before_screenshot": before_screenshot,
                "after_screenshot": after_screenshot,
                "diff_screenshot": diff_screenshot,
                "defects_found": len(defects),
                "defects": defects,
                "fix_applied": req.auto_heal and len(defects) > 0,
                "verification_passed": verification_passed,
                "summary": audit_record["summary"],
                "patch": patch_info,
                "target_url": audit_record["target_url"],
                "page_title": audit_record["page_title"]
            })
        except Exception as e:
            print(f"[OmniSight DB] Record save warning: {e}")

        return audit_record

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Device audit failed: {str(exc)}")

@router.post("/devices/multi-audit")
def audit_multi_device_fleet(req: MultiDeviceAuditRequest):
    """
    Audits a website across an entire fleet of devices simultaneously,
    aggregating responsive compliance and edge case defect radar.
    """
    navigator = get_navigator()
    target_url = req.target_url or "http://127.0.0.1:8000/test-app/index.html"
    fleet_results = {}
    scores = []
    total_defects = 0

    run_batch_id = f"fleet_{int(time.time())}"

    for dev_id in req.device_ids:
        dev_config = get_device_by_id(dev_id)
        try:
            capture = navigator.capture_device(
                device_config=dev_config,
                target_url=target_url,
                run_id=run_batch_id,
                suffix=""
            )
            score = capture["compliance_score"]
            scores.append(score)
            defects_count = len(capture["defects"])
            total_defects += defects_count

            fleet_results[dev_id] = {
                "device_name": dev_config["name"],
                "category": dev_config["category"],
                "width": dev_config["width"],
                "height": dev_config["height"],
                "compliance_score": score,
                "grade": capture["grade"],
                "defects_count": defects_count,
                "defects": capture["defects"],
                "screenshot": capture["screenshot_filename"],
                "checklist_summary": {
                    "passed": sum(1 for c in capture["checklist"] if c["status"] == "PASSED"),
                    "failed": sum(1 for c in capture["checklist"] if c["status"] == "FAILED"),
                    "warning": sum(1 for c in capture["checklist"] if c["status"] == "WARNING")
                }
            }
        except Exception as e:
            print(f"[OmniSight Fleet Audit] Failed for {dev_id}: {e}")

    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    return {
        "batch_id": run_batch_id,
        "target_url": target_url,
        "devices_audited": len(fleet_results),
        "fleet_compliance_score": avg_score,
        "total_defects_across_fleet": total_defects,
        "fleet_results": fleet_results,
        "overall_status": "compliant" if total_defects == 0 else "anomalies_detected"
    }

# Dynamic Monitoring Endpoints
@router.get("/monitors")
def list_monitors():
    """Lists all configured continuous monitoring jobs with health metrics."""
    return {
        "total": len(monitor_manager.list_monitors()),
        "monitors": monitor_manager.list_monitors()
    }

@router.post("/monitors")
def create_monitor(req: CreateMonitorRequest):
    """Creates a new dynamic continuous monitor."""
    return monitor_manager.create_monitor(req.model_dump())

@router.get("/monitors/{monitor_id}")
def get_monitor_details(monitor_id: str):
    """Returns monitor telemetry and history."""
    mon = monitor_manager.get_monitor(monitor_id)
    if not mon:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return mon

@router.post("/monitors/{monitor_id}/run-now")
def run_monitor_check_now(monitor_id: str):
    """Triggers an immediate live check across all monitored devices."""
    try:
        return monitor_manager.execute_check(monitor_id)
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Check execution failed: {str(exc)}")

@router.post("/monitors/{monitor_id}/toggle")
def toggle_monitor_state(monitor_id: str):
    """Pauses or resumes a monitor."""
    res = monitor_manager.toggle_monitor(monitor_id)
    if not res:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return res

@router.delete("/monitors/{monitor_id}")
def delete_monitor_job(monitor_id: str):
    """Deletes a monitor."""
    success = monitor_manager.delete_monitor(monitor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return {"deleted": True, "monitor_id": monitor_id}
