#!/usr/bin/env python3
"""
OmniSight Professional Autonomous Visual QA & Self-Healing CLI Runner
Executes multimodal inspection, 11-point dynamic compliance auditing,
responsive patch synthesis, and closed-loop visual verification.
"""

import sys
import os
import argparse
import json
import time
from pathlib import Path

# Ensure UTF-8 output across Windows PowerShell / CMD and Linux/macOS
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.agents.orchestrator import AgenticOrchestrator
from backend.storage.db import get_analytics_summary

# ANSI Color Codes & Formatting
class Palette:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    
    # Foreground colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # High-intensity foreground
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Backgrounds
    BG_DARK = "\033[48;5;235m"
    BG_GREEN = "\033[42m"
    BG_RED = "\033[41m"
    BG_BLUE = "\033[44m"

def supports_color() -> bool:
    """Checks whether the execution environment supports ANSI color codes."""
    if os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb":
        return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty() or os.name == "nt"

USE_COLOR = supports_color()

def c(text: str, color_code: str) -> str:
    """Wraps text in ANSI color code if supported."""
    return f"{color_code}{text}{Palette.RESET}" if USE_COLOR else text

def print_banner():
    div = "=" * 80
    print(c(div, Palette.CYAN))
    print(c("   OMNISIGHT AUTONOMOUS MULTIMODAL AUDIT & SELF-HEALING ENGINE", Palette.BRIGHT_CYAN + Palette.BOLD))
    print(c("   Visual QA • 11-Point Dynamic Edge Radar • Closed-Loop Unified Diff Patching", Palette.DIM))
    print(c(div, Palette.CYAN))

def print_stage_header(stage_num: int, total_stages: int, title: str, description: str):
    prefix = f"[{stage_num:02d}/{total_stages:02d}]"
    print(f"\n{c(prefix, Palette.BRIGHT_MAGENTA + Palette.BOLD)} {c(title.upper(), Palette.BRIGHT_WHITE + Palette.BOLD)}")
    print(f"  {c('→', Palette.MAGENTA)} {c(description, Palette.DIM)}")

def print_metric_badge(label: str, value: str, color: str = Palette.CYAN):
    print(f"  {c('•', Palette.DIM)} {label.ljust(26)}: {c(value, color + Palette.BOLD)}")

def print_edge_case_checklist(checklist: list):
    """Renders the 11-point dynamic compliance checklist as a structured terminal table."""
    col1_w = 40
    col2_w = 12
    col3_w = 42

    border_top = f"  ┌{'─'*col1_w}┬{'─'*col2_w}┬{'─'*col3_w}┐"
    border_mid = f"  ├{'─'*col1_w}┼{'─'*col2_w}┼{'─'*col3_w}┤"
    border_bot = f"  └{'─'*col1_w}┴{'─'*col2_w}┴{'─'*col3_w}┘"

    print(f"\n{c(border_top, Palette.DIM)}")
    header_col1 = "11-POINT DYNAMIC EDGE CHECK".ljust(col1_w - 2)
    header_col2 = "STATUS".ljust(col2_w - 2)
    header_col3 = "AUDIT OBSERVATION / METRIC".ljust(col3_w - 2)
    print(f"  {c('│', Palette.DIM)} {c(header_col1, Palette.BOLD)} {c('│', Palette.DIM)} {c(header_col2, Palette.BOLD)} {c('│', Palette.DIM)} {c(header_col3, Palette.BOLD)} {c('│', Palette.DIM)}")
    print(c(border_mid, Palette.DIM))
    
    for item in checklist:
        name_raw = item.get("name", "Unknown Check")[:col1_w - 2]
        status = item.get("status", "FAILED").upper()
        
        if status == "PASSED":
            status_text = "PASS [✓]".ljust(col2_w - 2)
            status_cell = c(status_text, Palette.BRIGHT_GREEN)
        elif status == "NOT_APPLICABLE":
            status_text = "N/A  [-]".ljust(col2_w - 2)
            status_cell = c(status_text, Palette.DIM)
        elif status == "WARNING":
            status_text = "WARN [!]".ljust(col2_w - 2)
            status_cell = c(status_text, Palette.BRIGHT_YELLOW)
        else:
            status_text = "FAIL [✗]".ljust(col2_w - 2)
            status_cell = c(status_text, Palette.BRIGHT_RED)
            
        expl = item.get("explanation") or "Nominal"
        expl_raw = expl[:col3_w - 2].ljust(col3_w - 2)
        
        name_cell = name_raw.ljust(col1_w - 2)
        print(f"  {c('│', Palette.DIM)} {name_cell} {c('│', Palette.DIM)} {status_cell} {c('│', Palette.DIM)} {expl_raw} {c('│', Palette.DIM)}")
        
    print(c(border_bot, Palette.DIM))

def print_unified_diff(diff_text: str):
    """Colorizes unified diff output (green for additions, red for deletions)."""
    if not diff_text or "No patch synthesized" in diff_text:
        print(f"  {c('No unified diff patch required.', Palette.DIM)}")
        return

    print(f"\n  {c('┌── Synthesized Unified Git Patch (.patch) ───────────────────────────┐', Palette.DIM)}")
    for line in diff_text.strip().splitlines():
        if line.startswith("+++") or line.startswith("---"):
            print(f"  {c('│', Palette.DIM)} {c(line, Palette.BOLD + Palette.YELLOW)}")
        elif line.startswith("@@"):
            print(f"  {c('│', Palette.DIM)} {c(line, Palette.CYAN)}")
        elif line.startswith("+"):
            print(f"  {c('│', Palette.DIM)} {c(line, Palette.BRIGHT_GREEN)}")
        elif line.startswith("-"):
            print(f"  {c('│', Palette.DIM)} {c(line, Palette.BRIGHT_RED)}")
        else:
            print(f"  {c('│', Palette.DIM)} {line}")
    print(f"  {c('└─────────────────────────────────────────────────────────────────────┘', Palette.DIM)}")

def run_audit(viewport: str = "mobile", url: Optional[str] = None, engine: Optional[str] = None, output_format: str = "rich"):
    start_time = time.time()
    print_banner()

    print(f"\n{c('INITIATING AUDIT RUN SESSION', Palette.BOLD)}")
    print_metric_badge("Target URL", url or "http://127.0.0.1:8000/test-app/index.html (Local Staging)")
    print_metric_badge("Viewport Profile", viewport.upper())
    print_metric_badge("Multimodal Vision Engine", (engine or "Autonomous Built-in / VLM Heuristic").title())
    print_metric_badge("Timestamp", time.strftime("%Y-%m-%d %H:%M:%S"))

    orchestrator = AgenticOrchestrator(headless=True)

    # 1. DISCOVERY & BROWSER NAVIGATION
    print_stage_header(1, 5, "Discovery & DOM Acquisition", "Spinning up isolated Playwright Chromium instance & harvesting DOM metrics")
    
    # 2. RUN SELF HEALING OR MATRIX AUDIT
    if viewport.lower() in ["all", "matrix"]:
        result = orchestrator.run_matrix_audit(target_url=url, engine=engine)
        viewport_label = "Multi-Device Matrix (Mobile + Tablet + Desktop)"
    else:
        result = orchestrator.run_self_healing_cycle(target_url=url, viewport_key=viewport, engine=engine)
        viewport_label = viewport.title()

    elapsed = round(time.time() - start_time, 2)

    # 3. VLM & SPATIAL ANOMALY DETECTION
    print_stage_header(2, 5, "Multimodal Spatial & Vision Diagnostics", "Evaluating visual bounds, spatial clipping, element hierarchy, and color tokens")
    defects = result.get("defects", [])
    defects_count = len(defects)
    
    if defects_count > 0:
        print(f"  {c('⚠ ATTENTION:', Palette.BRIGHT_YELLOW + Palette.BOLD)} Detected {defects_count} visual anomaly/anomalies violating responsive compliance:")
        for idx, defect in enumerate(defects, 1):
            severity = defect.get("severity", "HIGH").upper()
            sev_color = Palette.BRIGHT_RED if severity in ["CRITICAL", "HIGH"] else Palette.YELLOW
            elem = defect.get("element", "Target Element")
            dtype = defect.get("type", "Visual Anomaly")
            desc = defect.get("description", "Element layout anomaly detected.")
            
            print(f"\n    {c(f'Defect #{idx}', Palette.BOLD)} [{c(severity, sev_color + Palette.BOLD)}] {c(elem, Palette.CYAN)} ({dtype})")
            print(f"      {c('Root Cause:', Palette.DIM)} {desc}")
            if defect.get("proposed_fix"):
                fix_summary = " ".join(defect.get("proposed_fix", "").split())
                print(f"      {c('Proposed Fix:', Palette.DIM)} {c(fix_summary, Palette.GREEN)}")
    else:
        print(f"  {c('✓ PERFECT COMPLIANCE:', Palette.BRIGHT_GREEN + Palette.BOLD)} Zero visual defects detected. Viewport complies with design system specifications.")

    # 4. 11-POINT DYNAMIC COMPLIANCE RADAR
    print_stage_header(3, 5, "11-Point Dynamic Edge-Case Radar", "Comprehensive audit across accessibility, extreme aspect ratios, touch geometries, and layout integrity")
    checklist = result.get("checklist", [])
    compliance_score = result.get("compliance_score", 100.0)
    grade = result.get("grade", "A+ (Compliant)")
    
    print_metric_badge("Compliance Score", f"{compliance_score}%", Palette.BRIGHT_GREEN if compliance_score >= 85 else Palette.BRIGHT_RED)
    print_metric_badge("Certification Grade", grade, Palette.BRIGHT_GREEN if "A" in grade else Palette.BRIGHT_YELLOW)
    
    if checklist:
        print_edge_case_checklist(checklist)

    # 5. AUTONOMOUS PATCH SYNTHESIS & SELF-HEALING
    print_stage_header(4, 5, "Autonomous Patch Synthesis & Git Diff", "Synthesizing minimal responsive CSS rules and generating verified unified diff")
    patch = result.get("patch") or {}
    unified_diff = patch.get("unified_diff")
    if unified_diff:
        print_unified_diff(unified_diff)
    else:
        print(f"  {c('ℹ Status:', Palette.DIM)} Page layout is compliant; no corrective patch required.")

    # 6. CLOSED-LOOP VERIFICATION & PIXEL HEATMAP
    print_stage_header(5, 5, "Closed-Loop Verification & Gate Decision", "Re-evaluating DOM geometry in sandbox and generating pixel discrepancy heatmap")
    verification_passed = result.get("verification_passed", False)
    diff_stats = result.get("pixel_diff_stats") or {}
    diff_pct = diff_stats.get("diff_percentage", 0.0)
    
    print_metric_badge("Verification Status", "VERIFIED & RESOLVED [PASSED]" if verification_passed else "ACTION REQUIRED [FAILED]", 
                       Palette.BRIGHT_GREEN if verification_passed else Palette.BRIGHT_RED)
    print_metric_badge("Visual Pixel Diff Discrepancy", f"{diff_pct}%", Palette.BRIGHT_GREEN if diff_pct == 0.0 else Palette.YELLOW)
    print_metric_badge("Before Screenshot", result.get("before_screenshot", "N/A"))
    print_metric_badge("After Screenshot", result.get("after_screenshot", "N/A"))
    print_metric_badge("Pixel Heatmap Artifact", result.get("diff_screenshot", "N/A"))
    
    tokens = result.get("token_telemetry") or {}
    if tokens:
        print_metric_badge("VLM Tokens Consumed", f"{tokens.get('estimated_tokens_used', 'N/A')} tokens")
        print_metric_badge("Token Efficiency Savings", f"-{tokens.get('token_reduction_pct', 80)}% (Spatial Crop)", Palette.BRIGHT_GREEN)

    # EXECUTIVE SUMMARY FOOTER
    divider = "=" * 80
    print(f"\n{c(divider, Palette.CYAN)}")
    print(f"   {c('EXECUTIVE AUDIT SUMMARY & PR GATEWAY', Palette.BRIGHT_WHITE + Palette.BOLD)}")
    print(f"{c(divider, Palette.CYAN)}")
    print_metric_badge("Audit Run ID", result.get("id", "run_unknown"))
    print_metric_badge("Total Cycle Latency", f"{elapsed} seconds")
    print_metric_badge("Final Status", result.get("status", "unknown").upper(), Palette.BRIGHT_GREEN if result.get("status") in ["repaired", "passed"] else Palette.BRIGHT_RED)
    
    pr_payload = result.get("pr_payload")
    if pr_payload:
        print_metric_badge("Draft PR Branch", pr_payload.get("branch", "N/A"), Palette.BRIGHT_CYAN)
        print_metric_badge("Draft PR Title", pr_payload.get("title", "N/A"), Palette.WHITE)

    if verification_passed:
        print(f"\n  {c('>>> CI/CD QUALITY GATE: PASSED [READY FOR PRODUCTION MERGE] <<<', Palette.BG_GREEN + Palette.BLACK + Palette.BOLD)}")
    else:
        print(f"\n  {c('>>> CI/CD QUALITY GATE: BLOCKED [VISUAL REGRESSION DETECTED] <<<', Palette.BG_RED + Palette.WHITE + Palette.BOLD)}")
    print()

    # Raw JSON output mode if requested
    if output_format == "json":
        print(json.dumps(result, indent=2))

    return result

def main():
    parser = argparse.ArgumentParser(description="OmniSight Autonomous Audit & Self-Healing CLI")
    parser.add_argument("--viewport", "-v", default="mobile", choices=["mobile", "tablet", "desktop", "all", "matrix"], help="Target viewport tier")
    parser.add_argument("--url", "-u", default=None, help="Target URL (defaults to local staging store)")
    parser.add_argument("--engine", "-e", default=None, choices=["builtin", "gemini", "openai"], help="VLM engine")
    parser.add_argument("--json", action="store_true", help="Output full JSON payload")
    
    args = parser.parse_args()
    
    try:
        run_audit(
            viewport=args.viewport,
            url=args.url,
            engine=args.engine,
            output_format="json" if args.json else "rich"
        )
    except KeyboardInterrupt:
        print(f"\n{c('Audit cancelled by user.', Palette.YELLOW)}")
        sys.exit(130)
    except Exception as exc:
        print(f"\n{c(f'Fatal Audit Error: {exc}', Palette.BRIGHT_RED + Palette.BOLD)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
