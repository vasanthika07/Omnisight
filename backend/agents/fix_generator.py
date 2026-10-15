import difflib
import re
from pathlib import Path
from typing import Dict, Any, Tuple
from backend.config import PATCHES_DIR, TEST_APP_DIR

class FixGenerator:
    def __init__(self):
        self.css_file = TEST_APP_DIR / "checkout.css"

    def generate_css_patch(self, defect: Dict[str, Any]) -> str:
        """
        Synthesizes the targeted CSS patch rule.
        """
        element = defect.get("element", ".checkout-action-btn")
        proposed_rules = defect.get(
            "proposed_fix",
            "width: 100% !important; max-width: 100% !important; box-sizing: border-box !important;"
        )
        # Clean formatting
        clean_rules = "\n  ".join([r.strip() for r in proposed_rules.strip().split("\n") if r.strip()])
        patch_css = f"""{element} {{
  {clean_rules}
}}"""
        return patch_css

    def create_unified_diff(
        self,
        run_id: str,
        defect: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generates a standard Git unified diff patch for developer code review.
        """
        if not self.css_file.exists():
            return {
                "error": f"Target stylesheet {self.css_file} does not exist"
            }

        original_content = self.css_file.read_text(encoding="utf-8")
        
        # Regex replacement targeting the known buggy section
        # Replace fixed 520px with responsive 100%
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
            # Fallback: append or replace width
            repaired_content = original_content.replace(
                "width: 520px !important;",
                "width: 100% !important;\n  max-width: 100% !important;"
            )

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

    def reset_file_to_buggy_state(self) -> bool:
        """
        Resets the stylesheet back to intentional buggy state for repeated demo testing.
        """
        try:
            content = self.css_file.read_text(encoding="utf-8")
            pattern = r"/\* BUGGY_LINE_START \*/[\s\S]*?/\* BUGGY_LINE_END \*/"
            buggy_replacement = (
                "/* BUGGY_LINE_START */\n"
                "  width: 520px !important;\n"
                "  max-width: none !important;\n"
                "  /* BUGGY_LINE_END */"
            )
            if re.search(pattern, content):
                new_content = re.sub(pattern, buggy_replacement, content)
            else:
                new_content = content.replace(
                    "width: 100% !important;\n  max-width: 100% !important;",
                    "width: 520px !important;\n  max-width: none !important;"
                )
            self.css_file.write_text(new_content, encoding="utf-8")
            return True
        except Exception as e:
            print(f"[OmniSight FixGenerator] Reset failed: {e}")
            return False
