import time
from pathlib import Path
from typing import Dict, Any, Optional
from playwright.sync_api import sync_playwright
from backend.config import SCREENSHOTS_DIR, TEST_APP_DIR, VIEWPORTS
from backend.browser.dom_extractor import extract_dom_and_metrics

class BrowserNavigator:
    def __init__(self, headless: bool = True):
        self.headless = headless

    def get_default_test_app_url(self) -> str:
        index_file = TEST_APP_DIR / "index.html"
        return index_file.as_uri()

    def capture_viewport(
        self,
        viewport_key: str = "mobile",
        target_url: Optional[str] = None,
        run_id: str = "audit",
        suffix: str = ""
    ) -> Dict[str, Any]:
        """
        Navigates to the page at the given viewport, extracts DOM metrics, and saves screenshot.
        """
        url = target_url or self.get_default_test_app_url()
        vp_config = VIEWPORTS.get(viewport_key, VIEWPORTS["mobile"])
        
        screenshot_filename = f"{run_id}_{viewport_key}{suffix}.png"
        screenshot_path = SCREENSHOTS_DIR / screenshot_filename

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={"width": vp_config["width"], "height": vp_config["height"]},
                user_agent="Mozilla/5.0 (OmniSight Multimodal QA Agent 1.0)"
            )
            page = context.new_page()
            page.goto(url, wait_until="networkidle")
            
            # Allow animations or fonts to settle
            page.wait_for_timeout(350)
            
            # Extract DOM metadata and spatial metrics
            dom_metrics = extract_dom_and_metrics(page)
            
            # Save viewport screenshot
            page.screenshot(
                path=str(screenshot_path),
                full_page=False
            )
            
            browser.close()

        return {
            "viewport": viewport_key,
            "dimensions": vp_config,
            "screenshot_filename": screenshot_filename,
            "screenshot_path": str(screenshot_path),
            "dom_metrics": dom_metrics
        }

    def capture_all_viewports(
        self,
        target_url: Optional[str] = None,
        run_id: str = "audit"
    ) -> Dict[str, Any]:
        """
        Captures responsive screenshots across Mobile, Tablet, and Desktop viewports.
        """
        results = {}
        for vp_key in ["mobile", "tablet", "desktop"]:
            results[vp_key] = self.capture_viewport(
                viewport_key=vp_key,
                target_url=target_url,
                run_id=run_id
            )
        return results

    def verify_patch(
        self,
        css_patch: str,
        viewport_key: str = "mobile",
        target_url: Optional[str] = None,
        run_id: str = "audit"
    ) -> Dict[str, Any]:
        """
        Applies a candidate CSS patch in real-time inside the browser DOM and captures the after-state.
        """
        url = target_url or self.get_default_test_app_url()
        vp_config = VIEWPORTS.get(viewport_key, VIEWPORTS["mobile"])
        
        after_filename = f"{run_id}_{viewport_key}_after.png"
        after_path = SCREENSHOTS_DIR / after_filename

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={"width": vp_config["width"], "height": vp_config["height"]}
            )
            page = context.new_page()
            page.goto(url, wait_until="networkidle")
            
            # Inject candidate CSS patch directly into document head
            page.evaluate(f"""() => {{
                const styleEl = document.createElement('style');
                styleEl.id = 'omnisight-patch-injection';
                styleEl.textContent = `{css_patch}`;
                document.head.appendChild(styleEl);
            }}""")
            
            page.wait_for_timeout(300)
            
            # Extract verified DOM metrics
            new_dom_metrics = extract_dom_and_metrics(page)
            
            # Capture verified screenshot
            page.screenshot(
                path=str(after_path),
                full_page=False
            )
            
            browser.close()

        # Check if horizontal scrollbar / overflow is eliminated
        has_horizontal_overflow = new_dom_metrics.get("hasHorizontalScrollbar", False)
        
        # Check specific element overflow
        overflowing_elements = [
            el for el in new_dom_metrics.get("elements", [])
            if el.get("overflowsViewport", False)
        ]
        
        verification_passed = (not has_horizontal_overflow) and (len(overflowing_elements) == 0)

        return {
            "after_filename": after_filename,
            "after_path": str(after_path),
            "dom_metrics": new_dom_metrics,
            "verification_passed": verification_passed,
            "overflowing_elements_count": len(overflowing_elements)
        }
