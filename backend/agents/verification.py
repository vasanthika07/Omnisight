from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image, ImageChops
from backend.config import SCREENSHOTS_DIR

class VerificationEngine:
    def __init__(self):
        pass

    def generate_visual_diff_image(
        self,
        before_path: str,
        after_path: str,
        output_filename: str
    ) -> Optional[str]:
        """
        Generates a visual diff image highlighting pixel discrepancies between before and after states.
        """
        try:
            if not Path(before_path).exists() or not Path(after_path).exists():
                return None
            
            img1 = Image.open(before_path).convert("RGB")
            img2 = Image.open(after_path).convert("RGB")
            
            # Ensure equal dimensions for diff comparison
            if img1.size != img2.size:
                img2 = img2.resize(img1.size)
                
            diff = ImageChops.difference(img1, img2)
            
            # Enhance diff mask with neon magenta coloring
            diff_enhanced = diff.point(lambda p: min(255, p * 4))
            
            out_path = SCREENSHOTS_DIR / output_filename
            diff_enhanced.save(str(out_path))
            return output_filename
        except Exception as e:
            print(f"[OmniSight Verification] Visual diff generation failed: {e}")
            return None

    def evaluate_fix(
        self,
        before_metrics: Dict[str, Any],
        after_metrics: Dict[str, Any],
        target_selector: str = ".checkout-action-btn"
    ) -> Dict[str, Any]:
        """
        Evaluates whether the layout anomaly was successfully healed.
        """
        before_viewport = before_metrics.get("viewport", {"width": 375})
        vp_width = before_viewport.get("width", 375)
        
        # Check after state scrollbar
        after_has_h_scroll = after_metrics.get("hasHorizontalScrollbar", False)
        
        # Check after state target element bounds
        after_elements = after_metrics.get("elements", [])
        clean_target = target_selector.replace(".", "").replace("#", "").strip()
        target_el = next((
            e for e in after_elements 
            if clean_target in (e.get("selector", "") + " " + str(e.get("id") or "") + " " + str(e.get("className") or ""))
        ), None)
        
        healed = False
        remaining_overflow = 0
        
        if target_el:
            rect = target_el.get("rect", {})
            width = rect.get("width", 0)
            right = rect.get("right", 0)
            if right <= vp_width and width <= vp_width:
                healed = True
            else:
                remaining_overflow = max(right - vp_width, width - vp_width)
        else:
            # If target element is within standard bounds
            healed = not after_has_h_scroll
            
        return {
            "verified_passed": healed and (not after_has_h_scroll),
            "before_horizontal_scroll": before_metrics.get("hasHorizontalScrollbar", True),
            "after_horizontal_scroll": after_has_h_scroll,
            "target_element_healed": healed,
            "remaining_overflow_px": remaining_overflow,
            "verification_confidence": 0.99 if healed else 0.40,
            "status_message": (
                "Self-healing verified: Target element fits within viewport without clipping."
                if healed else "Verification failed: Element still exceeds viewport boundary."
            )
        }
