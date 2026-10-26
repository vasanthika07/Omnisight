import difflib
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.config import PATCHES_DIR, TEST_APP_DIR

SCENARIOS = {
    "overflow": {
        "id": "overflow",
        "name": "Mobile Viewport Clipping Anomaly",
        "category": "Responsiveness",
        "description": "520px fixed-width button clipping 375px mobile viewport boundary.",
        "target": ".checkout-action-btn",
        "severity": "CRITICAL"
    },
    "contrast": {
        "id": "contrast",
        "name": "Low Contrast Accessibility Violation",
        "category": "WCAG 1.4.3 AA",
        "description": "Dark gray text on dark background (#1e293b on #161b22, ratio 2.1:1).",
        "target": ".guarantee-text",
        "severity": "HIGH"
    },
    "touch_target": {
        "id": "touch_target",
        "name": "Sub-Standard Touch Target Size",
        "category": "WCAG 2.5.5",
        "description": "Checkout action button reduced to tiny 20px touch target.",
        "target": ".checkout-action-btn",
        "severity": "HIGH"
    },
    "zindex_overlap": {
        "id": "zindex_overlap",
        "name": "Floating Collision / Obscured CTA",
        "category": "RPA Automation",
        "description": "Floating promotional overlay blocking user checkout click target.",
        "target": ".promo-floating-overlay",
        "severity": "CRITICAL"
    }
}

class FixGenerator:
    def __init__(self):
        self.css_file = TEST_APP_DIR / "checkout.css"

    def list_scenarios(self) -> List[Dict[str, Any]]:
        return list(SCENARIOS.values())

    def generate_css_patch(self, defect: Dict[str, Any]) -> str:
        """
        Synthesizes the targeted CSS patch rule.
        """
        element = defect.get("element", ".checkout-action-btn")
        proposed_rules = defect.get(
            "proposed_fix",
            "width: 100% !important; max-width: 100% !important; box-sizing: border-box !important;"
        )
        clean_rules = "\n  ".join([r.strip() for r in proposed_rules.strip().split("\n") if r.strip()])
        patch_css = f"""{element} {{
  {clean_rules}
}}"""
        return patch_css

    def create_unified_diff(
        self,
        run_id: str,
        defect: Dict[str, Any],
        is_external: bool = False,
        target_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates a standard Git unified diff patch for developer code review.
        Supports both local repository files and external target websites.
        """
        if is_external:
            element = defect.get("element", "target-element")
            proposed_rules = defect.get(
                "proposed_fix",
                "width: 100% !important; max-width: 100% !important; box-sizing: border-box !important;"
            )
            clean_rules = "\n  ".join([r.strip() for r in proposed_rules.strip().split("\n") if r.strip()])
            injected_rule = f"{element} {{\n  {clean_rules}\n}}"
            
            domain_name = "external-site"
            if target_url:
                try:
                    from urllib.parse import urlparse
                    domain_name = urlparse(target_url).netloc or "external-site"
                except Exception:
                    domain_name = "external-site"
            
            virtual_path = f"styles/{domain_name}.css"
            orig_snippet = f"/* External Source: {target_url or 'Target Site'} */\n{element} {{\n  /* Original styling causing {defect.get('type', 'layout anomaly')} */\n}}\n"
            repaired_snippet = f"/* External Source: {target_url or 'Target Site'} */\n/* OmniSight Autonomous Self-Healing Patch */\n{element} {{\n  {clean_rules}\n}}\n"
            
            diff = difflib.unified_diff(
                orig_snippet.splitlines(keepends=True),
                repaired_snippet.splitlines(keepends=True),
                fromfile=f"a/{virtual_path}",
                tofile=f"b/{virtual_path}",
                n=3
            )
            unified_diff_str = "".join(diff)
            
            patch_file = PATCHES_DIR / f"{run_id}.diff"
            patch_file.write_text(unified_diff_str, encoding="utf-8")
            
            return {
                "patch_file": str(patch_file),
                "file_path": virtual_path,
                "target_selector": element,
                "original_css": orig_snippet,
                "repaired_css": repaired_snippet,
                "unified_diff": unified_diff_str,
                "css_injected_rule": injected_rule,
                "is_external": True
            }

        if not self.css_file.exists():
            return {
                "error": f"Target stylesheet {self.css_file} does not exist"
            }

        original_content = self.css_file.read_text(encoding="utf-8")
        defect_type = defect.get("type", "viewport_overflow")
        repaired_content = original_content

        if defect_type == "viewport_overflow":
            pattern = r"/\* BUGGY_LINE_START \*/[\s\S]*?/\* BUGGY_LINE_END \*/"
            replacement = (
                "/* BUGGY_LINE_START */\n"
                "  width: 100% !important;\n"
                "  max-width: 100% !important;\n"
                "  box-sizing: border-box !important;\n"
                "  /* BUGGY_LINE_END */"
            )
            if re.search(pattern, original_content):
                repaired_content = re.sub(pattern, replacement, original_content)
            else:
                repaired_content = original_content.replace(
                    "width: 520px !important;",
                    "width: 100% !important;\n  max-width: 100% !important;\n  box-sizing: border-box !important;"
                )
        elif defect_type == "element_obscured_overlap":
            # Hide the blocker overlay or make it static
            repaired_content = re.sub(
                r"\.promo-floating-overlay\s*\{[^}]*\}",
                ".promo-floating-overlay {\n  display: none !important;\n}",
                original_content
            )
        elif defect_type == "touch_target_too_small":
            pattern = r"/\* BUGGY_LINE_START \*/[\s\S]*?/\* BUGGY_LINE_END \*/"
            replacement = (
                "/* BUGGY_LINE_START */\n"
                "  width: 100% !important;\n"
                "  max-width: 100% !important;\n"
                "  min-height: 48px !important;\n"
                "  padding: 16px 24px !important;\n"
                "  box-sizing: border-box !important;\n"
                "  /* BUGGY_LINE_END */"
            )
            if re.search(pattern, original_content):
                repaired_content = re.sub(pattern, replacement, original_content)
        elif defect_type == "contrast_violation":
            repaired_content = original_content.replace(
                "color: #1e293b !important;",
                "color: #f0f6fc !important;"
            )
            if "color: #1e293b" not in original_content:
                repaired_content = original_content.replace(
                    "color: var(--text-secondary);",
                    "color: #f0f6fc !important;"
                )
        else:
            # Fallback CSS rule append or patch
            css_patch_rule = self.generate_css_patch(defect)
            repaired_content = original_content + f"\n\n/* OmniSight Self-Healing Patch */\n{css_patch_rule}\n"

        # Generate standard unified diff
        orig_lines = original_content.splitlines(keepends=True)
        rep_lines = repaired_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            orig_lines,
            rep_lines,
            fromfile="a/test-app/checkout.css",
            tofile="b/test-app/checkout.css",
            n=3
        )
        unified_diff_str = "".join(diff)

        # Save patch to artifacts
        patch_file = PATCHES_DIR / f"{run_id}.diff"
        patch_file.write_text(unified_diff_str, encoding="utf-8")

        return {
            "patch_file": str(patch_file),
            "file_path": "test-app/checkout.css",
            "target_selector": defect.get("element", ".checkout-action-btn"),
            "original_css": original_content,
            "repaired_css": repaired_content,
            "unified_diff": unified_diff_str,
            "css_injected_rule": self.generate_css_patch(defect)
        }

    def apply_patch_to_file(self, repaired_content: str) -> bool:
        """
        Writes the repaired content to the physical file in the workspace.
        """
        try:
            self.css_file.write_text(repaired_content, encoding="utf-8")
            return True
        except Exception as e:
            print(f"[OmniSight FixGenerator] Failed to write patch: {e}")
            return False

    def reset_file_to_clean_state(self) -> bool:
        """
        Resets stylesheet to 100% compliant, clean state with zero bugs.
        """
        try:
            content = self.css_file.read_text(encoding="utf-8")
            pattern = r"/\* BUGGY_LINE_START \*/[\s\S]*?/\* BUGGY_LINE_END \*/"
            clean_btn = (
                "/* BUGGY_LINE_START */\n"
                "  width: 100% !important;\n"
                "  max-width: 100% !important;\n"
                "  min-height: 48px !important;\n"
                "  box-sizing: border-box !important;\n"
                "  /* BUGGY_LINE_END */"
            )
            if re.search(pattern, content):
                content = re.sub(pattern, clean_btn, content)
            
            # Reset promo overlay
            content = re.sub(
                r"\.promo-floating-overlay\s*\{[^}]*\}",
                ".promo-floating-overlay {\n  display: none !important;\n}",
                content
            )
            # Reset guarantee text contrast
            content = content.replace("color: #1e293b !important;", "color: var(--text-secondary);")
            self.css_file.write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            print(f"[OmniSight FixGenerator] Clean reset failed: {e}")
            return False

    def reset_file_to_buggy_state(self) -> bool:
        """
        Resets the stylesheet back to intentional 520px buggy state for mobile overflow testing.
        """
        return self.inject_bug_scenario("overflow")

    def inject_bug_scenario(self, scenario_name: str) -> bool:
        """
        Injects a specific chaos test scenario into test-app/checkout.css.
        """
        try:
            # First reset to base clean state
            self.reset_file_to_clean_state()
            content = self.css_file.read_text(encoding="utf-8")
            scenario_key = scenario_name.lower().strip()

            if scenario_key in ["overflow", "button_overflow"]:
                pattern = r"/\* BUGGY_LINE_START \*/[\s\S]*?/\* BUGGY_LINE_END \*/"
                buggy_btn = (
                    "/* BUGGY_LINE_START */\n"
                    "  width: 520px !important;\n"
                    "  max-width: none !important;\n"
                    "  /* BUGGY_LINE_END */"
                )
                if re.search(pattern, content):
                    content = re.sub(pattern, buggy_btn, content)
                else:
                    content = content.replace(
                        "width: 100% !important;\n  max-width: 100% !important;",
                        "width: 520px !important;\n  max-width: none !important;"
                    )

            elif scenario_key in ["touch_target", "small_target"]:
                pattern = r"/\* BUGGY_LINE_START \*/[\s\S]*?/\* BUGGY_LINE_END \*/"
                tiny_btn = (
                    "/* BUGGY_LINE_START */\n"
                    "  width: 100% !important;\n"
                    "  max-width: 100% !important;\n"
                    "  height: 22px !important;\n"
                    "  min-height: 22px !important;\n"
                    "  padding: 2px 8px !important;\n"
                    "  font-size: 0.65rem !important;\n"
                    "  box-sizing: border-box !important;\n"
                    "  /* BUGGY_LINE_END */"
                )
                if re.search(pattern, content):
                    content = re.sub(pattern, tiny_btn, content)

            elif scenario_key in ["zindex_overlap", "overlay_collision", "overlap"]:
                overlay_active = (
                    ".promo-floating-overlay {\n"
                    "  display: flex !important;\n"
                    "  position: absolute !important;\n"
                    "  top: 0 !important;\n"
                    "  left: 0 !important;\n"
                    "  width: 100% !important;\n"
                    "  height: 56px !important;\n"
                    "  z-index: 9999 !important;\n"
                    "  align-items: center;\n"
                    "  justify-content: center;\n"
                    "}"
                )
                content = re.sub(r"\.promo-floating-overlay\s*\{[^}]*\}", overlay_active, content)

            elif scenario_key in ["contrast", "low_contrast"]:
                content = content.replace(
                    "color: var(--text-secondary);",
                    "color: #1e293b !important;"
                )

            self.css_file.write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            print(f"[OmniSight FixGenerator] Inject failed: {e}")
            return False
