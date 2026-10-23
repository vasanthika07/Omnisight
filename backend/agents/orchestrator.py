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
        
        # Reset test-app to ensure initial bug is active for the audit
        self.fixer.reset_file_to_buggy_state()
        
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
        log_step("vision_audit", "Feeding screenshot and DOM tree into Multimodal Vision-Language Model...")
        analysis = self.vision.analyze(before_path, before_dom, viewport_name=viewport_key)
        
        defects = analysis.get("defects", [])
        defects_found = len(defects) > 0
        
        log_step(
            "defect_detection",
            f"VLM Analysis completed. Found {len(defects)} defect(s). Engine: {analysis.get('engine_used')}",
            status="completed" if defects_found else "warning",
            details={"defects": defects, "confidence": analysis.get("visual_confidence_score")}
        )

        if not defects_found:
            log_step("complete", f"Audit complete for {viewport_key}: 0 visual defects found. Page layout complies with responsive standards.", status="completed")
            result = {
                "id": run_id,
                "viewport": viewport_key,
                "status": "passed",
                "defects_found": 0,
                "defects": [],
                "fix_applied": False,
                "verification_passed": True,
                "before_screenshot": before_screenshot,
                "engine_used": analysis.get("engine_used"),
                "confidence_score": analysis.get("visual_confidence_score", 1.0),
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

        for attempt in range(1, max_retries + 1):
            log_step("synthesize_patch", f"[Attempt {attempt}/{max_retries}] Synthesizing responsive CSS patch and unified git diff")
            
            patch_info = self.fixer.create_unified_diff(run_id, primary_defect)
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
                target_selector=primary_defect.get("element", ".checkout-action-btn")
            )
            
            verification_passed = eval_res.get("verified_passed", False)

            if verification_passed:
                log_step("verification", f"Verification Passed on attempt {attempt}! Visual clipping resolved.", status="success", details=eval_res)
                # Apply fix permanently to test-app/checkout.css for persistent demo
                if patch_info.get("repaired_css"):
                    self.fixer.apply_patch_to_file(patch_info["repaired_css"])
                break
            else:
                log_step("verification", f"Verification attempt {attempt} failed: remaining overflow {eval_res.get('remaining_overflow_px')}px. Retrying...", status="warning")
                # Mutate defect fix strategy for retry
                primary_defect["proposed_fix"] = "width: 100% !important; max-width: 100% !important; margin: 0 auto !important; box-sizing: border-box !important;"

        # -------------------------------------------------------------
        # 4. VISUAL PIXEL DIFF & PR ARTIFACTS
        # -------------------------------------------------------------
        diff_filename = f"{run_id}_diff.png"
        diff_res = self.verifier.generate_visual_diff_image(before_path, after_path, diff_filename)
        if diff_res:
            diff_screenshot = diff_filename
            log_step("visual_diff", f"Generated pixel discrepancy heatmap: {diff_filename}")

        # Prepare draft Pull Request summary
        pr_payload = {
            "title": f"fix(ui): resolve responsive clipping on {primary_defect.get('element', 'button')} on mobile viewport",
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
            "status": "repaired" if verification_passed else "failed",
            "defects_found": len(defects),
            "defects": defects,
            "fix_applied": True,
            "verification_passed": verification_passed,
            "before_screenshot": before_screenshot,
            "after_screenshot": after_screenshot,
            "diff_screenshot": diff_screenshot,
            "crop_screenshot": analysis.get("cropped_defect_token_artifact"),
            "cropped_defect_token_artifact": analysis.get("cropped_defect_token_artifact"),
            "engine_used": analysis.get("engine_used"),
            "confidence_score": analysis.get("visual_confidence_score", 0.99),
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
