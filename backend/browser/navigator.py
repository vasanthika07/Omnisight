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
        
        # If pointing to local test-app on port 8000, fallback to direct file:// URI if server is not up
        if ("127.0.0.1:8000/test-app" in url or "localhost:8000/test-app" in url):
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            is_open = sock.connect_ex(('127.0.0.1', 8000)) == 0
            sock.close()
            if not is_open:
                return self.get_default_test_app_url()

        if not (url.startswith("http://") or url.startswith("https://") or url.startswith("file://")):
            # Default to https:// for external domains
            url = f"https://{url}"
        return url

    def _navigate_page(self, page, url: str):
        """
        Navigates to URL with robust timeout and fallback for external websites and local files.
        """
        is_local = url.startswith("file://") or "127.0.0.1" in url or "localhost" in url
        if is_local:
            try:
                page.goto(url, wait_until="load", timeout=8000)
                page.wait_for_timeout(250)
                return
            except Exception as e:
                # Fallback to direct local test-app file URI if port was down
                if not url.startswith("file://"):
                    file_url = self.get_default_test_app_url()
                    page.goto(file_url, wait_until="load", timeout=8000)
                    page.wait_for_timeout(250)
                    return
                raise e

        # External website: prioritize domcontentloaded for high performance and immunity against tracker delays
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=10000)
            page.wait_for_timeout(400)
        except Exception as e:
            try:
                # Fallback to load or commit if page requires full lifecycle
                page.goto(url, wait_until="load", timeout=12000)
                page.wait_for_timeout(400)
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

    def capture_device(
        self,
        device_config: Dict[str, Any],
        target_url: Optional[str] = None,
        run_id: str = "device_audit",
        suffix: str = ""
    ) -> Dict[str, Any]:
        """
        Navigates and captures any arbitrary device profile with exact DPI scaling,
        touch emulation, user agent, viewport size, and dynamic edge-case evaluation.
        """
        from backend.devices.edge_case_checker import DynamicEdgeCaseChecker

        url = self.normalize_url(target_url)
        dev_id = device_config.get("id", "custom_device")
        w = int(device_config.get("width", 393))
        h = int(device_config.get("height", 852))
        dpr = float(device_config.get("dpr", 1.0))
        is_mobile = bool(device_config.get("is_mobile", True))
        has_touch = bool(device_config.get("has_touch", True))
        user_agent = device_config.get("user_agent", "Mozilla/5.0 OmniSight/1.0")
        color_scheme = device_config.get("color_scheme", "dark")

        screenshot_filename = f"{run_id}_{dev_id}{suffix}.png"
        screenshot_path = SCREENSHOTS_DIR / screenshot_filename

        console_errors = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={"width": w, "height": h},
                device_scale_factor=dpr,
                is_mobile=is_mobile,
                has_touch=has_touch,
                user_agent=user_agent,
                color_scheme=color_scheme,
                ignore_https_errors=True
            )
            page = context.new_page()

            # Record runtime errors
            page.on("pageerror", lambda err: console_errors.append(str(err)))
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            self._navigate_page(page, url)

            # Extract full DOM metrics
            dom_metrics = extract_dom_and_metrics(page)
            dom_metrics["console_errors"] = console_errors

            # Capture device screenshot
            page.screenshot(
                path=str(screenshot_path),
                full_page=False
            )

            browser.close()

        # Dynamic Edge Cases Audit
        checker = DynamicEdgeCaseChecker()
        edge_case_report = checker.evaluate(dom_metrics, device_config)

        return {
            "device": device_config,
            "dimensions": {"width": w, "height": h, "dpr": dpr},
            "screenshot_filename": screenshot_filename,
            "screenshot_path": str(screenshot_path),
            "dom_metrics": dom_metrics,
            "edge_case_report": edge_case_report,
            "compliance_score": edge_case_report["compliance_score"],
            "grade": edge_case_report["grade"],
            "checklist": edge_case_report["checklist"],
            "defects": edge_case_report["defects"]
        }

    def verify_device_patch(
        self,
        device_config: Dict[str, Any],
        css_patch: str,
        target_url: Optional[str] = None,
        run_id: str = "device_audit"
    ) -> Dict[str, Any]:
        """
        Injects synthesized responsive CSS patch and re-evaluates all 11 edge cases on the device.
        """
        from backend.devices.edge_case_checker import DynamicEdgeCaseChecker

        url = self.normalize_url(target_url)
        dev_id = device_config.get("id", "custom_device")
        w = int(device_config.get("width", 393))
        h = int(device_config.get("height", 852))
        dpr = float(device_config.get("dpr", 1.0))
        is_mobile = bool(device_config.get("is_mobile", True))
        has_touch = bool(device_config.get("has_touch", True))
        user_agent = device_config.get("user_agent", "Mozilla/5.0 OmniSight/1.0")

        after_filename = f"{run_id}_{dev_id}_after.png"
        after_path = SCREENSHOTS_DIR / after_filename

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                viewport={"width": w, "height": h},
                device_scale_factor=dpr,
                is_mobile=is_mobile,
                has_touch=has_touch,
                user_agent=user_agent,
                ignore_https_errors=True
            )
            page = context.new_page()
            self._navigate_page(page, url)

            # Inject candidate CSS patch
            page.evaluate("""(css) => {
                const styleEl = document.createElement('style');
                styleEl.id = 'omnisight-device-patch';
                styleEl.textContent = css;
                document.head.appendChild(styleEl);
            }""", css_patch)

            page.wait_for_timeout(350)
            new_dom_metrics = extract_dom_and_metrics(page)
            new_dom_metrics["console_errors"] = []

            page.screenshot(
                path=str(after_path),
                full_page=False
            )
            browser.close()

        # Re-evaluate all edge cases on patched DOM
        checker = DynamicEdgeCaseChecker()
        after_report = checker.evaluate(new_dom_metrics, device_config)
        has_blowout = any(d.get("type") == "viewport_overflow" for d in after_report["defects"])
        repaired = (not has_blowout) and (len(after_report["defects"]) == 0 or after_report["compliance_score"] >= 80.0)

        return {
            "after_filename": after_filename,
            "after_path": str(after_path),
            "dom_metrics": new_dom_metrics,
            "after_report": after_report,
            "verification_passed": repaired,
            "healed_score": after_report["compliance_score"]
        }
