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

    def normalize_url(self, target_url: Optional[str]) -> str:
        if not target_url or not str(target_url).strip():
            return self.get_default_test_app_url()
        url = str(target_url).strip()
        if not (url.startswith("http://") or url.startswith("https://") or url.startswith("file://")):
            # Default to https:// for external domains
            url = f"https://{url}"
        return url

    def _navigate_page(self, page, url: str):
        """
        Navigates to URL with robust timeout and fallback for external websites.
        """
        is_local = url.startswith("file://") or "127.0.0.1" in url or "localhost" in url
        if is_local:
            page.goto(url, wait_until="networkidle", timeout=10000)
            page.wait_for_timeout(250)
            return

        # External website: try load event first with 18s timeout
        try:
            page.goto(url, wait_until="load", timeout=18000)
            page.wait_for_timeout(600)
        except Exception as e:
            try:
                # Fallback to domcontentloaded if external trackers/ads delay network idle/load
                page.goto(url, wait_until="domcontentloaded", timeout=12000)
                page.wait_for_timeout(500)
            except Exception as inner_e:
                print(f"[OmniSight Navigator] External site navigation warning for {url}: {inner_e}")

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
        url = self.normalize_url(target_url)
        vp_config = VIEWPORTS.get(viewport_key, VIEWPORTS["mobile"])
        
        screenshot_filename = f"{run_id}_{viewport_key}{suffix}.png"
        screenshot_path = SCREENSHOTS_DIR / screenshot_filename

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={"width": vp_config["width"], "height": vp_config["height"]},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OmniSight/1.0",
                ignore_https_errors=True
            )
            page = context.new_page()
            self._navigate_page(page, url)
            
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
        url = self.normalize_url(target_url)
        vp_config = VIEWPORTS.get(viewport_key, VIEWPORTS["mobile"])
        
        after_filename = f"{run_id}_{viewport_key}_after.png"
        after_path = SCREENSHOTS_DIR / after_filename

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={"width": vp_config["width"], "height": vp_config["height"]},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OmniSight/1.0",
                ignore_https_errors=True
            )
            page = context.new_page()
            self._navigate_page(page, url)
            
            # Inject candidate CSS patch directly into document head
            page.evaluate("""(css) => {
                const styleEl = document.createElement('style');
                styleEl.id = 'omnisight-patch-injection';
                styleEl.textContent = css;
                document.head.appendChild(styleEl);
            }""", css_patch)
            
            page.wait_for_timeout(350)
            
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
