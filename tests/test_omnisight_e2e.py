"""
OmniSight End-to-End Automated Test Suite
Validates the complete autonomous visual QA loop:
- Browser navigation & DOM extraction
- Vision analyzer defect detection & Pillow token-crop
- Responsive CSS patch synthesis & Unified Diff generation
- Closed-loop Playwright verification & Pixel Diff heatmap
- SQLite database persistence with timeline & diagnostics
- GitHub PR Manager branch preparation & dispatch
- CI/CD build webhook gateway
"""

import sys
import os
import unittest
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.agents.orchestrator import AgenticOrchestrator
from backend.agents.fix_generator import FixGenerator
from backend.github_integration.pr_manager import GitHubPRManager
from backend.storage.db import get_recent_runs, get_run_by_id, save_audit_run
from backend.routes.webhook import active_jobs, execute_background_ci_audit

class TestOmniSightE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orchestrator = AgenticOrchestrator(headless=True)
        cls.fixer = FixGenerator()
        cls.pr_manager = GitHubPRManager()

    def test_01_reset_stylesheet(self):
        """Verifies resetting stylesheet to intentional buggy state."""
        success = self.fixer.reset_file_to_buggy_state()
        self.assertTrue(success, "Failed to reset stylesheet to buggy state")
        content = self.fixer.css_file.read_text(encoding="utf-8")
        self.assertIn("520px", content, "Stylesheet does not contain fixed 520px width")

    def test_02_mobile_self_healing_cycle(self):
        """Verifies autonomous Plan -> Execute -> Evaluate -> Verify loop on mobile."""
        # Ensure initial buggy state
        self.fixer.reset_file_to_buggy_state()
        
        result = self.orchestrator.run_self_healing_cycle(viewport_key="mobile", max_retries=2)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "repaired")
        self.assertTrue(result["verification_passed"], "Verification failed on mobile self-healing")
        self.assertGreaterEqual(result["defects_found"], 1, "Expected at least 1 layout defect on mobile")
        
        # Verify deduplication (exact button element detected once)
        button_defects = [d for d in result["defects"] if "checkout" in d.get("element", "").lower()]
        self.assertEqual(len(button_defects), 1, "Expected exactly 1 deduplicated button defect")
        
        # Verify patch info
        patch = result.get("patch")
        self.assertIsNotNone(patch, "Patch information missing")
        self.assertIn("width: 100%", patch.get("repaired_css", ""), "Repaired CSS does not contain 100% width")
        self.assertIn("--- a/test-app/checkout.css", patch.get("unified_diff", ""), "Unified diff header missing")
        
        # Verify diff screenshot generated
        self.assertIsNotNone(result.get("diff_screenshot"), "Pixel diff heatmap screenshot was not generated")
        
        # Verify timeline populated
        timeline = result.get("timeline", [])
        self.assertGreaterEqual(len(timeline), 7, "Timeline should have at least 7 execution steps")
        step_names = [s["step"] for s in timeline]
        self.assertIn("plan", step_names)
        self.assertIn("browse", step_names)
        self.assertIn("vision_audit", step_names)
        self.assertIn("defect_detection", step_names)
        self.assertIn("synthesize_patch", step_names)
        self.assertIn("execute_fix", step_names)
        self.assertIn("verification", step_names)
        self.assertIn("complete", step_names)

        # Verify DB persistence
        db_record = get_run_by_id(result["id"])
        self.assertIsNotNone(db_record, "Run was not saved in SQLite DB")
        self.assertEqual(len(db_record.get("timeline", [])), len(timeline), "Persisted timeline length mismatch")
        self.assertIsNotNone(db_record.get("patch"), "Persisted patch missing in SQLite")

    def test_03_desktop_audit_clean_pass(self):
        """Verifies desktop audit reports zero visual defects and status passed."""
        result = self.orchestrator.run_self_healing_cycle(viewport_key="desktop")
        
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["defects_found"], 0)
        self.assertTrue(result["verification_passed"])
        self.assertIsNotNone(result.get("engine_used"))

    def test_04_pr_dispatch_manager(self):
        """Verifies Pull Request generation and branch preparation."""
        branch = "omnisight/test-automated-pr-unit"
        title = "fix(ui): responsive test button fix"
        body = "Automated test body with proof"
        
        pr_result = self.pr_manager.create_pull_request(
            branch_name=branch,
            title=title,
            body=body,
            file_path="test-app/checkout.css",
            repaired_content="/* repaired content */"
        )
        
        self.assertTrue(pr_result.get("success"), f"PR creation failed: {pr_result}")
        self.assertIn("pr_number", pr_result)
        self.assertIn("pr_url", pr_result)
        self.assertEqual(pr_result.get("branch"), branch)

    def test_05_ci_webhook_integration(self):
        """Verifies CI/CD webhook job queueing and background completion."""
        job_id = "job_ci_unit_test"
        active_jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "created_at": 1000
        }
        
        execute_background_ci_audit(job_id, staging_url=None)
        
        self.assertIn(job_id, active_jobs)
        self.assertEqual(active_jobs[job_id]["status"], "completed")
        self.assertIn("result", active_jobs[job_id])
        self.assertEqual(active_jobs[job_id]["result"]["status"], "repaired")

if __name__ == "__main__":
    unittest.main(verbosity=2)
