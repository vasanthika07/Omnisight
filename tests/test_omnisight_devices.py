"""
OmniSight Dynamic Any-Device & Live Fleet Monitoring Automated Test Suite
Validates:
- Any-device emulation & dynamic custom device geometry
- 11 Universal Dynamic Edge Cases inspection radar
- Multi-device fleet simultaneous auditing
- Live fleet continuous monitor telemetry & immediate execution
- Generated patch & unified diff work deliverables
"""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.devices.registry import get_all_devices, get_device_by_id, create_custom_device, DEVICE_PRESETS
from backend.devices.edge_case_checker import DynamicEdgeCaseChecker
from backend.devices.monitor import monitor_manager, get_navigator
from backend.agents.fix_generator import FixGenerator

class TestOmniSightAnyDevice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.navigator = get_navigator()
        cls.checker = DynamicEdgeCaseChecker()
        cls.fixer = FixGenerator()

    def test_01_device_catalog_and_presets(self):
        """Verifies device catalog contains comprehensive presets across all categories."""
        devices = get_all_devices()
        self.assertGreaterEqual(len(devices), 15, "Expected at least 15 standard presets in registry")
        
        categories = {d["category"] for d in devices}
        self.assertIn("phones", categories)
        self.assertIn("tablets", categories)
        self.assertIn("desktops", categories)
        self.assertIn("foldables", categories)

        iphone = get_device_by_id("iphone_15_pro")
        self.assertEqual(iphone["width"], 393)
        self.assertEqual(iphone["height"], 852)
        self.assertTrue(iphone["has_touch"])

    def test_02_custom_device_dynamic_spec(self):
        """Verifies custom dynamic device specification builder."""
        custom_spec = {
            "width": 412,
            "height": 915,
            "dpr": 2.6,
            "is_mobile": True,
            "has_touch": True,
            "orientation": "landscape",
            "color_scheme": "dark"
        }
        device_config = create_custom_device(custom_spec)
        # In landscape orientation, width and height are dynamically adjusted
        self.assertEqual(device_config["width"], 915)
        self.assertEqual(device_config["height"], 412)
        self.assertEqual(device_config["orientation"], "landscape")
        self.assertEqual(device_config["category"], "custom")

    def test_03_sixteen_dynamic_edge_and_rare_cases_evaluation(self):
        """Verifies evaluation of all 16 universal edge and rare cases on mobile."""
        device_config = get_device_by_id("iphone_15_pro")
        mock_dom = {
            "documentScrollWidth": 520,
            "hasHorizontalScrollbar": True,
            "elements": [
                {
                    "tagName": "button",
                    "selector": "#checkout-btn",
                    "text": "Complete Purchase",
                    "rect": {"x": 20, "y": 200, "width": 520, "height": 38, "right": 540},
                    "computed": {"fontSize": "16px", "color": "rgb(255, 255, 255)", "backgroundColor": "#10b981"}
                }
            ],
            "overlaps": [],
            "media_items": [],
            "meta_info": {"hasViewportMeta": True, "userScalable": True},
            "console_errors": []
        }
        report = self.checker.evaluate(mock_dom, device_config)
        self.assertIsNotNone(report)
        self.assertIn("compliance_score", report)
        self.assertIn("grade", report)
        self.assertIn("performance_levels", report)
        self.assertIn("weak_areas", report)
        self.assertEqual(len(report["performance_levels"]), 5, "Should evaluate all 5 performance levels")
        self.assertGreaterEqual(len(report["weak_areas"]), 1, "Should identify at least 1 weak area for blowout")
        self.assertEqual(len(report["checklist"]), 16, "Should evaluate all 16 universal edge and rare cases")
        
        # Verify all 16 check IDs are present
        check_ids = [c["id"] for c in report["checklist"]]
        expected_ids = [
            "layout_blowout",
            "element_clipping",
            "touch_target",
            "zindex_collision",
            "color_contrast",
            "viewport_meta",
            "typography_elasticity",
            "unconstrained_media",
            "extreme_aspect_ratio",
            "safe_area_occlusion",
            "runtime_console_errors",
            "foldable_hinge_split",
            "dynamic_viewport_height_trapping",
            "tap_target_proximity",
            "accessible_name_missing",
            "scroll_trapping_overflow"
        ]
        for exp_id in expected_ids:
            self.assertIn(exp_id, check_ids, f"Expected check '{exp_id}' in checklist")

        blowout = next(c for c in report["checklist"] if c["id"] == "layout_blowout")
        self.assertEqual(blowout["status"], "FAILED")

    def test_04_live_device_capture_and_self_healing(self):
        """Verifies live device capture, defect detection, and patch verification on intentional staging bug."""
        self.fixer.reset_file_to_buggy_state()
        device_config = get_device_by_id("iphone_se")
        
        capture_res = self.navigator.capture_device(
            device_config=device_config,
            target_url=None,
            run_id="test_unit_dev"
        )
        self.assertIsNotNone(capture_res)
        self.assertGreaterEqual(len(capture_res["defects"]), 1)
        
        # Synthesize CSS patch
        primary_defect = capture_res["defects"][0]
        patch_css = self.fixer.generate_css_patch(primary_defect)
        self.assertIn("width: 100%", patch_css)

        # Verify patch on device
        verify_res = self.navigator.verify_device_patch(
            device_config=device_config,
            css_patch=patch_css,
            target_url=None,
            run_id="test_unit_dev"
        )
        self.assertTrue(verify_res["verification_passed"])
        self.assertGreaterEqual(verify_res["healed_score"], 80.0)

    def test_05_fleet_continuous_monitor_execution(self):
        """Verifies fleet continuous monitor registration and immediate check execution."""
        monitors = monitor_manager.list_monitors()
        self.assertGreaterEqual(len(monitors), 1)
        
        default_mon = monitors[0]
        check_res = monitor_manager.execute_check(default_mon["id"])
        self.assertIsNotNone(check_res)
        self.assertIn("overall_score", check_res)
        self.assertIn("status", check_res)
        self.assertIn("latency_ms", check_res)
        self.assertIn("device_results", check_res)

        updated_mon = monitor_manager.get_monitor(default_mon["id"])
        self.assertIsNotNone(updated_mon.get("last_score"))

    def test_06_external_website_device_audit(self):
        """Verifies dynamic edge case inspection, compliance scoring, and auto-heal on an external website."""
        from backend.routes.devices import audit_any_device, DeviceAuditRequest

        req = DeviceAuditRequest(
            device_id="iphone_15_pro",
            target_url="https://example.com",
            auto_heal=True
        )
        res = audit_any_device(req)
        self.assertIsNotNone(res)
        self.assertTrue(res.get("is_external"))
        self.assertEqual(res.get("target_url"), "https://example.com")
        self.assertIn("compliance_score", res)
        self.assertIn("grade", res)
        self.assertEqual(len(res.get("checklist", [])), 16, "All 16 universal edge and rare cases should be evaluated")
        self.assertIsNotNone(res.get("before_screenshot"))

        # If defects were found on external site (e.g. small touch targets), verify patch generation
        if res.get("defects_found", 0) > 0:
            self.assertIsNotNone(res.get("patch"))
            self.assertTrue(res.get("verification_passed"))

    def test_07_external_website_multi_device_fleet(self):
        """Verifies multi-device fleet audit on an external website across phones and tablets."""
        from backend.routes.devices import audit_multi_device_fleet, MultiDeviceAuditRequest

        req = MultiDeviceAuditRequest(
            device_ids=["iphone_15_pro", "ipad_air"],
            target_url="https://example.com"
        )
        res = audit_multi_device_fleet(req)
        self.assertIsNotNone(res)
        self.assertEqual(res.get("target_url"), "https://example.com")
        self.assertEqual(res.get("devices_audited"), 2)
        self.assertIn("fleet_compliance_score", res)
        self.assertIn("iphone_15_pro", res.get("fleet_results", {}))
        self.assertIn("ipad_air", res.get("fleet_results", {}))

    def test_08_foldable_device_hinge_bisection_detection(self):
        """Verifies detection of rare foldable physical hinge seam bisection on dual-screen devices."""
        foldable_config = get_device_by_id("galaxy_z_fold5_unfolded")
        self.assertIsNotNone(foldable_config)
        self.assertEqual(foldable_config["category"], "foldables")
        hinge_x = foldable_config["width"] // 2  # 816 // 2 = 408

        # Mock DOM with a CTA that directly bisects the central hinge
        mock_dom = {
            "documentScrollWidth": foldable_config["width"],
            "hasHorizontalScrollbar": False,
            "elements": [
                {
                    "tagName": "button",
                    "selector": "#bisecting-hero-cta",
                    "text": "Submit Application",
                    "rect": {"x": 350, "y": 300, "width": 120, "height": 48, "right": 470},
                    "isInteractive": True,
                    "hasAccessibleName": True,
                    "computed": {"fontSize": "16px", "color": "#ffffff", "backgroundColor": "#2563eb"}
                }
            ],
            "overlaps": [],
            "media_items": [],
            "meta_info": {"hasViewportMeta": True, "userScalable": True},
            "console_errors": []
        }
        report = self.checker.evaluate(mock_dom, foldable_config)
        self.assertIsNotNone(report)
        hinge_chk = next(c for c in report["checklist"] if c["id"] == "foldable_hinge_split")
        self.assertEqual(hinge_chk["status"], "FAILED")
        self.assertIn("bisects the physical foldable screen hinge seam", hinge_chk["explanation"])
        self.assertEqual(hinge_chk["metrics"]["hinge_coordinate"], f"x = {hinge_x}px")
        # Verify Level 4 incorporates this check
        lvl4 = next(l for l in report["performance_levels"] if l["level"] == 4)
        self.assertIn(lvl4["status"], ["FAIL", "WARN"])

if __name__ == "__main__":
    unittest.main()
