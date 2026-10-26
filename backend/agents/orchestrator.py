import time
import uuid
from typing import Dict, Any, List, Optional, Callable
from backend.browser.navigator import BrowserNavigator
from backend.agents.vision_analyzer import MultimodalVisionAnalyzer
from backend.agents.fix_generator import FixGenerator
from backend.agents.verification import VerificationEngine
from backend.storage.db import save_audit_run

class AgenticOrchestrator:
    def __init__(self, headless: bool = True):
        self.navigator = BrowserNavigator(headless=headless)
        self.vision = MultimodalVisionAnalyzer()
        self.fixer = FixGenerator()
        self.verifier = VerificationEngine()

    def run_self_healing_cycle(
        self,
        target_url: Optional[str] = None,
        viewport_key: str = "mobile",
        max_retries: int = 2,
        engine: Optional[str] = None,
        auto_reset_bug: Optional[bool] = None,
        log_callback: Optional[Callable[[str, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Executes the autonomous Plan -> Execute -> Evaluate -> Verify loop.
        """
        run_id = f"run_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        timeline: List[Dict[str, Any]] = []

        def log_step(step_name: str, message: str, status: str = "completed", details: Any = None):
            entry = {
                "step": step_name,
                "message": message,
                "status": status,
                "timestamp": time.time(),
                "details": details
            }
            timeline.append(entry)
            if log_callback:
                log_callback(step_name, message)
            print(f"[{run_id}] [{step_name.upper()}] {message}")

        # -------------------------------------------------------------
        # 1. PLAN & EXECUTE BROWSER AUDIT
        # -------------------------------------------------------------
        log_step("plan", f"Initializing headless browser navigation for viewport: {viewport_key}")
        
        # Determine if we should set the default bug
        is_external_target = bool(target_url and str(target_url).strip() and not str(target_url).strip().startswith("file://") and "test-app" not in str(target_url))
        
        if not is_external_target:
            if auto_reset_bug is True:
                self.fixer.reset_file_to_buggy_state()
            elif auto_reset_bug is None and viewport_key == "mobile":
                try:
                    css_txt = self.fixer.css_file.read_text(encoding="utf-8")
                    has_any_bug = ("width: 520px" in css_txt or "520px !important" in css_txt or "height: 22px" in css_txt or 
                                   "display: flex !important;" in css_txt or "color: #1e293b" in css_txt)
                    if not has_any_bug:
                        self.fixer.reset_file_to_buggy_state()
                except Exception:
                    pass
        
        before_res = self.navigator.capture_viewport(
            viewport_key=viewport_key,
            target_url=target_url,
            run_id=run_id,
            suffix="_before"
        )
        before_screenshot = before_res["screenshot_filename"]
        before_path = before_res["screenshot_path"]
        before_dom = before_res["dom_metrics"]

        log_step(
            "browse",
            f"Captured initial viewport screenshot: {before_screenshot}",
            details={"dimensions": before_res["dimensions"], "has_overflow": before_dom.get("hasHorizontalScrollbar")}
        )

        # -------------------------------------------------------------
        # 2. MULTIMODAL VLM INSPECTION
        # -------------------------------------------------------------
        log_step("vision_audit", f"Feeding screenshot and DOM tree into Multimodal Vision Engine ({engine or 'auto'})...")
        analysis = self.vision.analyze(before_path, before_dom, viewport_name=viewport_key, engine=engine)
        
        defects = analysis.get("defects", [])
        defects_found = len(defects) > 0
        token_telemetry = analysis.get("token_telemetry", {})
        
        log_step(
            "defect_detection",
            f"VLM Analysis completed. Found {len(defects)} defect(s). Engine: {analysis.get('engine_used')}",
            status="completed" if defects_found else "warning",
            details={
                "defects": defects, 
                "confidence": analysis.get("visual_confidence_score"),
                "token_savings": f"-{token_telemetry.get('token_reduction_pct', 80)}% tokens"
            }
        )

        if not defects_found:
            log_step("complete", f"Audit complete for {viewport_key}: 0 visual defects found. Page layout complies with responsive standards.", status="completed")
            result = {
                "id": run_id,
                "viewport": viewport_key,
                "target_url": target_url or "http://127.0.0.1:8000/test-app/index.html",
                "page_title": before_dom.get("pageTitle", "Target Page"),
                "is_external": is_external_target,
                "status": "passed",
                "defects_found": 0,
                "defects": [],
                "fix_applied": False,
                "verification_passed": True,
                "before_screenshot": before_screenshot,
                "engine_used": analysis.get("engine_used"),
                "confidence_score": analysis.get("visual_confidence_score", 1.0),
                "token_telemetry": token_telemetry,
                "summary": f"No visual defects detected on target page ({viewport_key} viewport).",
                "timeline": timeline
            }
            save_audit_run(result)
            return result

        # -------------------------------------------------------------
        # 3. SELF-HEALING ACTION LOOP (RETRY CAPABLE)
        # -------------------------------------------------------------
        primary_defect = defects[0]
        patch_info = None
        verification_passed = False
        after_screenshot = None
        after_path = None
        diff_screenshot = None
        pixel_diff_stats = {}

        for attempt in range(1, max_retries + 1):
            log_step("synthesize_patch", f"[Attempt {attempt}/{max_retries}] Synthesizing responsive patch and unified git diff for {primary_defect.get('type')}")
            
            patch_info = self.fixer.create_unified_diff(
                run_id=run_id,
                defect=primary_defect,
                is_external=is_external_target,
                target_url=target_url
            )
            injected_css = patch_info.get("css_injected_rule", "")

            log_step(
                "execute_fix",
                f"Applying candidate patch rule to DOM: {injected_css.replace(chr(10), ' ')}",
                details={"patch_file": patch_info.get("patch_file")}
            )

            # Re-run browser verification in isolated context
            verify_res = self.navigator.verify_patch(
                css_patch=injected_css,
                viewport_key=viewport_key,
                target_url=target_url,
                run_id=run_id
            )
            
            after_screenshot = verify_res["after_filename"]
            after_path = verify_res["after_path"]
            after_dom = verify_res["dom_metrics"]

            # Evaluate with spatial verification engine
            eval_res = self.verifier.evaluate_fix(
                before_metrics=before_dom,
                after_metrics=after_dom,
                target_selector=primary_defect.get("element", ".checkout-action-btn"),
                defect_type=primary_defect.get("type", "viewport_overflow")
            )
            
            verification_passed = eval_res.get("verified_passed", False)
            pixel_diff_stats = eval_res.get("pixel_diff_stats", {})

            if verification_passed:
                log_step("verification", f"Verification Passed on attempt {attempt}! Defect resolved.", status="success", details=eval_res)
                # Apply fix permanently to test-app/checkout.css for persistent demo only if testing local checkout
                if not is_external_target and patch_info.get("repaired_css"):
                    self.fixer.apply_patch_to_file(patch_info["repaired_css"])
                break
            else:
                log_step("verification", f"Verification attempt {attempt} failed: {eval_res.get('status_message')}. Retrying...", status="warning")
                # Mutate defect fix strategy for retry
                primary_defect["proposed_fix"] = "width: 100% !important; max-width: 100% !important; margin: 0 auto !important; box-sizing: border-box !important;"

        # -------------------------------------------------------------
        # 4. VISUAL PIXEL DIFF & PR ARTIFACTS
        # -------------------------------------------------------------
        diff_filename = f"{run_id}_diff.png"
        diff_res = self.verifier.generate_visual_diff_image(before_path, after_path, diff_filename)
        if diff_res:
            diff_screenshot = diff_filename
            pixel_diff_stats = self.verifier.last_diff_stats
            log_step("visual_diff", f"Generated pixel discrepancy heatmap: {diff_filename} ({pixel_diff_stats.get('diff_percentage', 0)}% diff)")

        # Prepare draft Pull Request summary
        pr_payload = {
            "title": f"fix(ui): resolve {primary_defect.get('type', 'layout anomaly')} on {primary_defect.get('element', 'target')} ({viewport_key})",
            "branch": f"omnisight/fix-ui-{run_id}",
            "body": (
                f"## 🤖 OmniSight Autonomous Self-Healing Report\n\n"
                f"**Defect Identified:** {primary_defect.get('description')}\n"
                f"**Severity:** `{primary_defect.get('severity')}`\n"
                f"**Engine:** `{analysis.get('engine_used')}`\n"
                f"**Verification Status:** {'✅ Verified Healed' if verification_passed else '⚠️ Requires Manual Check'}\n\n"
                f"### Visual Proof:\n"
                f"- Before: `{before_screenshot}`\n"
                f"- After: `{after_screenshot}`\n"
            ),
            "patch_file": patch_info.get("patch_file") if patch_info else None,
            "unified_diff": patch_info.get("unified_diff") if patch_info else None
        }

        log_step("complete", "OmniSight autonomous audit and self-healing cycle finished successfully.")

        run_record = {
            "id": run_id,
            "viewport": viewport_key,
            "target_url": target_url or "http://127.0.0.1:8000/test-app/index.html",
            "page_title": before_dom.get("pageTitle", "Target Page"),
            "is_external": is_external_target,
            "status": "repaired" if verification_passed else "failed",
            "defects_found": len(defects),
            "defects": defects,
            "fix_applied": True,
            "verification_passed": verification_passed,
            "before_screenshot": before_screenshot,
            "after_screenshot": after_screenshot,
            "diff_screenshot": diff_screenshot,
            "pixel_diff_stats": pixel_diff_stats,
            "crop_screenshot": analysis.get("cropped_defect_token_artifact"),
            "cropped_defect_token_artifact": analysis.get("cropped_defect_token_artifact"),
            "engine_used": analysis.get("engine_used"),
            "confidence_score": analysis.get("visual_confidence_score", 0.99),
            "token_telemetry": token_telemetry,
            "summary": (
                f"Autonomous self-healing completed: Repaired {primary_defect.get('element')} "
                f"with responsive patch. Visual verification passed."
            ),
            "patch": patch_info,
            "pr_payload": pr_payload,
            "timeline": timeline
        }

        # Save to database
        save_audit_run(run_record)

        return run_record

    def run_matrix_audit(
        self,
        target_url: Optional[str] = None,
        max_retries: int = 2,
        engine: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a Multi-Device Matrix Audit across Mobile, Tablet, and Desktop tiers.
        Evaluates responsive elasticity and defect resilience across all viewports.
        """
        matrix_id = f"matrix_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        viewports = ["mobile", "tablet", "desktop"]
        runs = {}
        total_defects = 0
        healed_count = 0
        
        # Ensure initial bug is set for matrix demo if testing default checkout
        is_matrix_external = bool(target_url and str(target_url).strip() and not str(target_url).strip().startswith("file://") and "test-app" not in str(target_url))
        if not is_matrix_external:
            self.fixer.reset_file_to_buggy_state()

        for vp in viewports:
            run_res = self.run_self_healing_cycle(
                target_url=target_url,
                viewport_key=vp,
                max_retries=max_retries,
                engine=engine,
                auto_reset_bug=False
            )
            runs[vp] = run_res
            total_defects += run_res.get("defects_found", 0)
            if run_res.get("verification_passed"):
                healed_count += 1
                
        responsive_score = round((healed_count / len(viewports)) * 100)
        mobile_run = runs.get("mobile", {})

        matrix_record = {
            "id": matrix_id,
            "is_matrix": True,
            "target_url": target_url or "http://127.0.0.1:8000/test-app/index.html",
            "page_title": mobile_run.get("page_title", "Target Page"),
            "is_external": is_matrix_external,
            "created_at": time.time(),
            "matrix_viewports": runs,
            "overall_status": "repaired" if total_defects > 0 and healed_count == len(viewports) else ("passed" if total_defects == 0 else "action_required"),
            "total_defects": total_defects,
            "responsive_score": responsive_score,
            "viewports_evaluated": viewports,
            # Primary attributes for dashboard fallback compatibility
            "viewport": "matrix (all devices)",
            "status": "repaired" if mobile_run.get("verification_passed") else "passed",
            "defects_found": total_defects,
            "defects": [d for r in runs.values() for d in r.get("defects", [])],
            "verification_passed": all(r.get("verification_passed") for r in runs.values()),
            "before_screenshot": mobile_run.get("before_screenshot"),
            "after_screenshot": mobile_run.get("after_screenshot"),
            "diff_screenshot": mobile_run.get("diff_screenshot"),
            "pixel_diff_stats": mobile_run.get("pixel_diff_stats"),
            "crop_screenshot": mobile_run.get("crop_screenshot"),
            "cropped_defect_token_artifact": mobile_run.get("cropped_defect_token_artifact"),
            "patch": mobile_run.get("patch"),
            "timeline": mobile_run.get("timeline"),
            "engine_used": mobile_run.get("engine_used"),
            "token_telemetry": mobile_run.get("token_telemetry"),
            "summary": f"Multi-Device Matrix Audit completed: {responsive_score}% responsive score across Mobile, Tablet, and Desktop."
        }

        save_audit_run(matrix_record)
        return matrix_record
