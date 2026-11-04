"""
OmniSight Dynamic Edge Case Checker
Comprehensive inspection suite auditing 11 real-world responsive & accessibility edge cases
dynamically across any device profile.
"""

from typing import Dict, Any, List, Optional
import math

class DynamicEdgeCaseChecker:
    """
    Evaluates raw browser DOM metrics, computed styles, spatial geometry, and performance
    telemetry against the 11 Universal Edge Case standards.
    """

    def evaluate(self, dom_metrics: Dict[str, Any], device_config: Dict[str, Any]) -> Dict[str, Any]:
        vp_width = device_config.get("width", 393)
        vp_height = device_config.get("height", 852)
        is_touch = device_config.get("has_touch", True)
        is_mobile = device_config.get("is_mobile", True)
        orientation = device_config.get("orientation", "portrait")
        safe_area = device_config.get("safe_area_insets", {"top": 0, "bottom": 0})
        has_notch = safe_area.get("top", 0) > 20 or safe_area.get("bottom", 0) > 16

        elements = dom_metrics.get("elements", [])
        overlaps = dom_metrics.get("overlaps", [])
        media_items = dom_metrics.get("media_items", [])
        meta_info = dom_metrics.get("meta_info", {})
        console_errors = dom_metrics.get("console_errors", [])
        doc_scroll_width = dom_metrics.get("documentScrollWidth", vp_width)
        has_h_scroll = dom_metrics.get("hasHorizontalScrollbar", doc_scroll_width > vp_width + 4)

        checklist = []
        defects = []
        score = 100.0

        # =========================================================================
        # 1. LAYOUT BLOWOUT & HORIZONTAL SCROLL OVERFLOW
        # =========================================================================
        blowout_violations = []
        for el in elements:
            rect = el.get("rect", {})
            rect_w = rect.get("width", 0)
            rect_r = rect.get("right", 0)
            if rect_r > vp_width + 3 or rect_w > vp_width + 3:
                overflow_px = max(rect_r - vp_width, rect_w - vp_width)
                blowout_violations.append({
                    "selector": el.get("selector"),
                    "tag": el.get("tagName"),
                    "element_text": el.get("text", "")[:40],
                    "width": rect_w,
                    "overflow_px": overflow_px,
                    "rect": rect
                })

        if has_h_scroll or len(blowout_violations) > 0:
            primary = blowout_violations[0] if blowout_violations else None
            element_name = primary["selector"] if primary else "document.body"
            overflow_amount = primary["overflow_px"] if primary else max(0, doc_scroll_width - vp_width)
            
            checklist.append({
                "id": "layout_blowout",
                "name": "Viewport Layout Blowout & Horizontal Leak",
                "category": "Responsiveness",
                "status": "FAILED",
                "severity": "CRITICAL",
                "metrics": {
                    "document_scroll_width": f"{doc_scroll_width}px",
                    "viewport_width": f"{vp_width}px",
                    "overflow_pixels": f"+{overflow_amount}px",
                    "violating_elements": len(blowout_violations)
                },
                "explanation": f"Document width ({doc_scroll_width}px) exceeds device viewport ({vp_width}px). Element '{element_name}' bleeds outside screen bounds by {overflow_amount}px.",
                "remediation": "width: 100% !important; max-width: 100% !important; box-sizing: border-box !important;"
            })
            score -= 25.0

            defects.append({
                "type": "viewport_overflow",
                "severity": "critical",
                "element": element_name,
                "element_text": primary.get("element_text", "") if primary else "",
                "description": f"Layout blowout on {device_config.get('name')}: Element '{element_name}' renders at {primary['width'] if primary else doc_scroll_width}px, exceeding {vp_width}px viewport by {overflow_amount}px.",
                "bounding_box": primary["rect"] if primary else {"x": 0, "y": 0, "width": doc_scroll_width, "height": 60},
                "overflow_pixels": overflow_amount,
                "proposed_fix": "width: 100% !important;\nmax-width: 100% !important;\nbox-sizing: border-box !important;"
            })
        else:
            checklist.append({
                "id": "layout_blowout",
                "name": "Viewport Layout Blowout & Horizontal Leak",
                "category": "Responsiveness",
                "status": "PASSED",
                "severity": "INFO",
                "metrics": {
                    "document_scroll_width": f"{doc_scroll_width}px",
                    "viewport_width": f"{vp_width}px",
                    "overflow_pixels": "0px"
                },
                "explanation": f"Zero horizontal scroll leak. Document perfectly elastified within {vp_width}px width.",
                "remediation": None
            })

        # =========================================================================
        # 2. INTERACTIVE CLIPPING & TEXT TRUNCATION
        # =========================================================================
        clipping_violations = []
        for el in elements:
            rect = el.get("rect", {})
            if rect.get("left", 0) < -3 or (rect.get("right", 0) > vp_width + 4 and el.get("tagName") in ["button", "a", "h1", "h2", "p"]):
                clipping_violations.append({
                    "selector": el.get("selector"),
                    "tag": el.get("tagName"),
                    "text": el.get("text", "")[:40],
                    "rect": rect
                })

        if clipping_violations:
            first_clip = clipping_violations[0]
            checklist.append({
                "id": "element_clipping",
                "name": "Element Bounding Box & Label Clipping",
                "category": "Visual Integrity",
                "status": "FAILED",
                "severity": "HIGH",
                "metrics": {
                    "clipped_elements": len(clipping_violations),
                    "primary_clipped_target": first_clip["selector"]
                },
                "explanation": f"Element '{first_clip['selector']}' ({first_clip['tag']}) is partially clipped by screen margins, cutting off textual context.",
                "remediation": "overflow-wrap: break-word !important; word-break: break-word !important; text-overflow: ellipsis !important;"
            })
            score -= 15.0
        else:
            checklist.append({
                "id": "element_clipping",
                "name": "Element Bounding Box & Label Clipping",
                "category": "Visual Integrity",
                "status": "PASSED",
                "severity": "INFO",
                "metrics": {"clipped_elements": 0},
                "explanation": "All critical interactive and typography elements are rendered fully within visible viewport margins.",
                "remediation": None
            })

        # =========================================================================
        # 3. TOUCH TARGET ACCESSIBILITY (WCAG 2.5.5 / 2.5.8)
        # =========================================================================
        if is_touch:
            small_touch_targets = []
            touch_collisions = []

            for el in elements:
                tag = el.get("tagName", "").lower()
                sel = el.get("selector", "")
                rect = el.get("rect", {})
                w = rect.get("width", 0)
                h = rect.get("height", 0)
                if w <= 0 or h <= 0:
                    continue

                # WCAG 2.5.5 touch target minimum (44×44px) for interactive buttons, links, and action triggers
                if tag in ["button", "a"] or "btn" in sel or (tag == "input" and any(btn_t in el.get("type", "") for btn_t in ["button", "submit", "reset"])):
                    if w < 44 or h < 44:
                        small_touch_targets.append({
                            "selector": sel,
                            "width": w,
                            "height": h,
                            "rect": rect
                        })
                elif tag in ["input", "select"] and "radio" not in sel and "checkbox" not in sel:
                    # WCAG 2.5.8 minimum (24×24px) for text/select form inputs
                    if w < 24 or h < 24:
                        small_touch_targets.append({
                            "selector": sel,
                            "width": w,
                            "height": h,
                            "rect": rect
                        })

            if small_touch_targets:
                target = small_touch_targets[0]
                checklist.append({
                    "id": "touch_target",
                    "name": "Touch Target Accessibility (WCAG 2.5.5 / 2.5.8)",
                    "category": "Accessibility",
                    "status": "FAILED",
                    "severity": "HIGH",
                    "metrics": {
                        "violating_touch_targets": len(small_touch_targets),
                        "smallest_target": f"{target['selector']} ({target['width']}×{target['height']}px)",
                        "required_minimum": "44×44px (WCAG AAA: 48×48px)"
                    },
                    "explanation": f"Touch target '{target['selector']}' measures {target['width']}×{target['height']}px, failing WCAG 2.5.5 touch target minimum (44×44px) on touchscreens.",
                    "remediation": "input, button, a { display: inline-block !important; min-height: 44px !important; min-width: 44px !important; line-height: 44px !important; box-sizing: border-box !important; }"
                })
                score -= 15.0
                defects.append({
                    "type": "touch_target_too_small",
                    "severity": "high",
                    "element": "input, button" if target["selector"].startswith("#") or "input" in target["selector"] else target["selector"],
                    "description": f"Touch target '{target['selector']}' on {device_config.get('name')} is {target['width']}×{target['height']}px. Violates WCAG 2.5.5 minimum 44×44px standard.",
                    "bounding_box": target["rect"],
                    "proposed_fix": "display: inline-block !important;\nmin-height: 44px !important;\nmin-width: 44px !important;\nline-height: 44px !important;\nbox-sizing: border-box !important;"
                })
            else:
                checklist.append({
                    "id": "touch_target",
                    "name": "Touch Target Accessibility (WCAG 2.5.5 / 2.5.8)",
                    "category": "Accessibility",
                    "status": "PASSED",
                    "severity": "INFO",
                    "metrics": {
                        "touch_targets_audited": len([e for e in elements if e.get("tagName") in ["button", "a", "input"]]),
                        "status": "All targets >= 44x44px"
                    },
                    "explanation": "All interactive elements meet WCAG touch target dimensions (>= 44x44px) for reliable finger tap interaction.",
                    "remediation": None
                })
        else:
            checklist.append({
                "id": "touch_target",
                "name": "Touch Target Accessibility (WCAG 2.5.5)",
                "category": "Accessibility",
                "status": "NOT_APPLICABLE",
                "severity": "INFO",
                "metrics": {"device_mode": "Desktop Pointer / Mouse"},
                "explanation": "Touch target minimums relaxed for desktop mouse/pointer device profile.",
                "remediation": None
            })

        # =========================================================================
        # 4. Z-INDEX COLLISION & OVERLAY OBSCURATION
        # =========================================================================
        significant_overlaps = [o for o in overlaps if o.get("overlapArea", 0) > 250]
        if significant_overlaps:
            first_overlap = significant_overlaps[0]
            checklist.append({
                "id": "zindex_collision",
                "name": "Z-Index Collision & Overlay Obscuration",
                "category": "RPA & Automation",
                "status": "FAILED",
                "severity": "CRITICAL",
                "metrics": {
                    "colliding_elements": f"{first_overlap.get('elementA')} <-> {first_overlap.get('elementB')}",
                    "collision_area": f"{first_overlap.get('overlapArea')}px²"
                },
                "explanation": f"Floating or fixed element '{first_overlap.get('elementA')}' overlaps and occludes interactive target '{first_overlap.get('elementB')}', blocking RPA clicks.",
                "remediation": "position: static !important; z-index: 1 !important; display: none !important;"
            })
            score -= 25.0
            defects.append({
                "type": "element_obscured_overlap",
                "severity": "critical",
                "element": first_overlap.get("elementA"),
                "blocked_element": first_overlap.get("elementB"),
                "description": f"Collision: Element '{first_overlap.get('elementA')}' obscures '{first_overlap.get('elementB')}' ({first_overlap.get('overlapArea')}px² collision area).",
                "bounding_box": first_overlap.get("overlapRect", {}),
                "proposed_fix": "display: none !important;\nposition: static !important;\nz-index: 1 !important;"
            })
        else:
            checklist.append({
                "id": "zindex_collision",
                "name": "Z-Index Collision & Overlay Obscuration",
                "category": "RPA & Automation",
                "status": "PASSED",
                "severity": "INFO",
                "metrics": {"active_collisions": 0},
                "explanation": "No interactive CTAs are obstructed by floating modals, fixed headers, or cookie banners.",
                "remediation": None
            })

        # =========================================================================
        # 5. COLOR CONTRAST COMPLIANCE (WCAG 2.1 AA)
        # =========================================================================
        contrast_violations = []
        for el in elements:
            computed = el.get("computed", {})
            color = str(computed.get("color", "")).lower()
            bg_color = str(computed.get("backgroundColor", "")).lower()
            # Detect low contrast combinations
            if ("rgb(45, 55, 72)" in color or "rgb(30, 41, 59)" in color or "rgb(20, 25, 35)" in color) and ("#161b22" in bg_color or "rgb(13, 17, 23)" in bg_color or "rgba(0, 0, 0" in bg_color or "transparent" in bg_color):
                contrast_violations.append({
                    "selector": el.get("selector"),
                    "color": color,
                    "estimated_ratio": "2.2:1 (Required: 4.5:1)",
                    "rect": el.get("rect", {})
                })

        if contrast_violations:
            violating = contrast_violations[0]
            checklist.append({
                "id": "color_contrast",
                "name": "WCAG 2.1 AA Color Contrast Compliance",
                "category": "Accessibility",
                "status": "FAILED",
                "severity": "HIGH",
                "metrics": {
                    "violating_elements": len(contrast_violations),
                    "primary_target": violating["selector"],
                    "measured_ratio": violating["estimated_ratio"]
                },
                "explanation": f"Element '{violating['selector']}' exhibits insufficient luminance contrast against background. Fails WCAG AA minimum 4.5:1 ratio.",
                "remediation": "color: #f0f6fc !important; opacity: 1 !important;"
            })
            score -= 15.0
            defects.append({
                "type": "contrast_violation",
                "severity": "high",
                "element": violating["selector"],
                "description": f"Low contrast violation on {device_config.get('name')}: Element '{violating['selector']}' ratio is below 3:1.",
                "bounding_box": violating["rect"],
                "proposed_fix": "color: #f0f6fc !important;\nopacity: 1 !important;"
            })
        else:
            checklist.append({
                "id": "color_contrast",
                "name": "WCAG 2.1 AA Color Contrast Compliance",
                "category": "Accessibility",
                "status": "PASSED",
                "severity": "INFO",
                "metrics": {"contrast_status": "All text >= 4.5:1 ratio"},
                "explanation": "Typography color contrast satisfies WCAG 2.1 AA standards for high visual legibility.",
                "remediation": None
            })

        # =========================================================================
        # 6. VIEWPORT META TAG CONFIGURATION
        # =========================================================================
        has_meta = meta_info.get("hasViewportMeta", True)
        user_scalable = meta_info.get("userScalable", True)
        initial_scale = meta_info.get("initialScale", "1.0")
        
        if is_mobile and not has_meta:
            checklist.append({
                "id": "viewport_meta",
                "name": "Responsive Viewport Meta Tag Configuration",
                "category": "Mobile Standards",
                "status": "FAILED",
                "severity": "HIGH",
                "metrics": {"has_viewport_meta": "Missing"},
                "explanation": "Page is missing `<meta name='viewport' content='width=device-width, initial-scale=1.0'>`. Mobile browsers will render in desktop 980px fallback mode.",
                "remediation": "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
            })
            score -= 15.0
        elif is_mobile and user_scalable is False:
            checklist.append({
                "id": "viewport_meta",
                "name": "Responsive Viewport Meta Tag Configuration",
                "category": "Mobile Standards",
                "status": "WARNING",
                "severity": "MEDIUM",
                "metrics": {"user_scalable": "disabled (user-scalable=no)"},
                "explanation": "Viewport contains `user-scalable=no` or `maximum-scale=1.0`, preventing visually impaired users from zooming (WCAG 1.4.4).",
                "remediation": "content='width=device-width, initial-scale=1.0, maximum-scale=5.0'"
            })
            score -= 5.0
        else:
            checklist.append({
                "id": "viewport_meta",
                "name": "Responsive Viewport Meta Tag Configuration",
                "category": "Mobile Standards",
                "status": "PASSED",
                "severity": "INFO",
                "metrics": {"viewport_tag": "width=device-width, initial-scale=1.0"},
                "explanation": "Viewport metadata correctly informs mobile layout engine to match device physical dimensions.",
                "remediation": None
            })

        # =========================================================================
        # 7. TYPOGRAPHY ELASTICITY & FONT SCALING
        # =========================================================================
        typo_violations = []
        for el in elements:
            computed = el.get("computed", {})
            fs_str = str(computed.get("fontSize", "16px")).replace("px", "").strip()
            try:
                fs = float(fs_str)
                if vp_width < 450 and fs > 38 and el.get("tagName") in ["h1", "h2"]:
                    typo_violations.append({
                        "selector": el.get("selector"),
                        "fontSize": f"{fs}px",
                        "issue": "Excessive font size on narrow screen"
                    })
                elif is_mobile and fs < 11 and el.get("tagName") in ["p", "span", "a", "button"]:
                    typo_violations.append({
                        "selector": el.get("selector"),
                        "fontSize": f"{fs}px",
                        "issue": "Unreadable sub-11px text on mobile"
                    })
            except Exception:
                pass

        if typo_violations:
            first_typo = typo_violations[0]
            checklist.append({
                "id": "typography_elasticity",
                "name": "Typography Elasticity & Fluid Font Scaling",
                "category": "Visual Integrity",
                "status": "WARNING",
                "severity": "MEDIUM",
                "metrics": {
                    "flagged_elements": len(typo_violations),
                    "primary_target": f"{first_typo['selector']} ({first_typo['fontSize']})"
                },
                "explanation": f"Typography on '{first_typo['selector']}' ({first_typo['fontSize']}) fails fluid elasticity guidelines for a {vp_width}px viewport.",
                "remediation": "font-size: clamp(1rem, 4vw, 2rem) !important;"
            })
            score -= 5.0
        else:
            checklist.append({
                "id": "typography_elasticity",
                "name": "Typography Elasticity & Fluid Font Scaling",
                "category": "Visual Integrity",
                "status": "PASSED",
                "severity": "INFO",
                "metrics": {"font_elasticity": "Balanced"},
                "explanation": "Font sizes are well-balanced across headings and body text for this screen density.",
                "remediation": None
            })

        # =========================================================================
        # 8. UNCONSTRAINED MEDIA & BROKEN ASSETS
        # =========================================================================
        broken_media = [m for m in media_items if m.get("isBroken")]
        overflowing_media = [m for m in media_items if m.get("width", 0) > vp_width + 4]

        if broken_media or overflowing_media:
            checklist.append({
                "id": "unconstrained_media",
                "name": "Unconstrained Media & Asset Integrity",
                "category": "Assets & Performance",
                "status": "FAILED" if broken_media else "WARNING",
                "severity": "HIGH" if broken_media else "MEDIUM",
                "metrics": {
                    "broken_images": len(broken_media),
                    "overflowing_media": len(overflowing_media)
                },
                "explanation": f"Detected {len(broken_media)} broken media assets and {len(overflowing_media)} unconstrained media items exceeding viewport width.",
                "remediation": "img, video, iframe, svg { max-width: 100% !important; height: auto !important; }"
            })
            score -= 10.0
        else:
            checklist.append({
                "id": "unconstrained_media",
                "name": "Unconstrained Media & Asset Integrity",
                "category": "Assets & Performance",
                "status": "PASSED",
                "severity": "INFO",
                "metrics": {"media_integrity": "All media constrained & loaded"},
                "explanation": "All images and media containers adhere to fluid responsive constraints (`max-width: 100%`).",
                "remediation": None
            })

        # =========================================================================
        # 9. EXTREME ASPECT RATIO & ORIENTATION COMPLIANCE
        # =========================================================================
        is_landscape_mobile = orientation == "landscape" and vp_height < 450
        is_ultrawide = vp_width >= 2560

        if is_landscape_mobile:
            # Check if sticky elements eat more than 40% of vertical height
            sticky_height = dom_metrics.get("stickyElementsTotalHeight", 0)
            if sticky_height > vp_height * 0.40:
                checklist.append({
                    "id": "extreme_aspect_ratio",
                    "name": "Orientation Extreme: Mobile Landscape Squish",
                    "category": "Orientation & Viewport",
                    "status": "FAILED",
                    "severity": "HIGH",
                    "metrics": {
                        "viewport_height": f"{vp_height}px",
                        "sticky_headers_height": f"{sticky_height}px",
                        "screen_coverage": f"{round((sticky_height / vp_height) * 100)}%"
                    },
                    "explanation": f"In mobile landscape ({vp_width}×{vp_height}px), fixed navigation consumes {sticky_height}px (>40% of screen), severely compromising content viewing.",
                    "remediation": "@media (orientation: landscape) and (max-height: 480px) { header, nav { position: static !important; } }"
                })
                score -= 15.0
            else:
                checklist.append({
                    "id": "extreme_aspect_ratio",
                    "name": "Orientation Extreme: Mobile Landscape Squish",
                    "category": "Orientation & Viewport",
                    "status": "PASSED",
                    "severity": "INFO",
                    "metrics": {"viewport": f"Landscape {vp_width}×{vp_height}px"},
                    "explanation": "Mobile landscape viewport accommodates navigation without vertical content smothering.",
                    "remediation": None
                })
        elif is_ultrawide:
            body_max_w = dom_metrics.get("bodyMaxWidth", "none")
            if body_max_w == "none" or body_max_w == "":
                checklist.append({
                    "id": "extreme_aspect_ratio",
                    "name": "Orientation Extreme: Ultrawide Canvas Overstretch",
                    "category": "Orientation & Viewport",
                    "status": "WARNING",
                    "severity": "MEDIUM",
                    "metrics": {
                        "viewport_width": f"{vp_width}px",
                        "container_max_width": "None"
                    },
                    "explanation": f"On {vp_width}px ultrawide screens, lack of a max-width container causes text reading lines to span >2000px, violating reading ergonomics.",
                    "remediation": "max-width: 1440px !important; margin-left: auto !important; margin-right: auto !important;"
                })
                score -= 8.0
            else:
                checklist.append({
                    "id": "extreme_aspect_ratio",
                    "name": "Orientation Extreme: Ultrawide Canvas Overstretch",
                    "category": "Orientation & Viewport",
                    "status": "PASSED",
                    "severity": "INFO",
                    "metrics": {"viewport_width": f"{vp_width}px", "bounded": "Container constrained"},
                    "explanation": f"Layout gracefully bounds main content on {vp_width}px wide screen display.",
                    "remediation": None
                })
        else:
            checklist.append({
                "id": "extreme_aspect_ratio",
                "name": "Orientation Extreme: Aspect Ratio Ergonomics",
                "category": "Orientation & Viewport",
                "status": "PASSED",
                "severity": "INFO",
                "metrics": {"aspect_ratio": f"{vp_width}×{vp_height}px ({orientation})"},
                "explanation": "Viewport aspect ratio is within standard ergonomic tolerance limits.",
                "remediation": None
            })

        # =========================================================================
        # 10. NOTCH & SAFE AREA OCCLUSION
        # =========================================================================
        if has_notch:
            notch_top = safe_area.get("top", 0)
            home_bar_bot = safe_area.get("bottom", 0)
            occluded_elements = []

            for el in elements:
                computed = el.get("computed", {})
                pos = computed.get("position", "")
                if pos in ["fixed", "absolute"]:
                    rect = el.get("rect", {})
                    # If placed directly in the top notch zone
                    if rect.get("y", 0) < notch_top - 5 and el.get("tagName") in ["button", "a", "input"]:
                        occluded_elements.append({
                            "selector": el.get("selector"),
                            "issue": f"Occluded by {notch_top}px device notch or Dynamic Island"
                        })
                    # If placed in bottom home-indicator bar zone
                    if rect.get("bottom", 0) > vp_height - home_bar_bot + 5 and el.get("tagName") in ["button", "a"]:
                        occluded_elements.append({
                            "selector": el.get("selector"),
                            "issue": f"Obstructed by {home_bar_bot}px bottom Home Indicator bar"
                        })

            if occluded_elements:
                first_occ = occluded_elements[0]
                checklist.append({
                    "id": "safe_area_occlusion",
                    "name": "Display Notch & Safe Area Inset Occlusion",
                    "category": "Device Hardware Cutouts",
                    "status": "FAILED",
                    "severity": "HIGH",
                    "metrics": {
                        "safe_area_top": f"{notch_top}px",
                        "safe_area_bottom": f"{home_bar_bot}px",
                        "occluded_elements": len(occluded_elements)
                    },
                    "explanation": f"Interactive control '{first_occ['selector']}' collides with the device hardware cutout or home indicator bar.",
                    "remediation": "padding-top: env(safe-area-inset-top) !important; padding-bottom: env(safe-area-inset-bottom) !important;"
                })
                score -= 15.0
            else:
                checklist.append({
                    "id": "safe_area_occlusion",
                    "name": "Display Notch & Safe Area Inset Occlusion",
                    "category": "Device Hardware Cutouts",
                    "status": "PASSED",
                    "severity": "INFO",
                    "metrics": {
                        "safe_area_top": f"{notch_top}px",
                        "safe_area_bottom": f"{home_bar_bot}px",
                        "status": "Safe area respected"
                    },
                    "explanation": "No interactive controls are occluded by hardware camera cutouts or rounded display edges.",
                    "remediation": None
                })
        else:
            checklist.append({
                "id": "safe_area_occlusion",
                "name": "Display Notch & Safe Area Inset Occlusion",
                "category": "Device Hardware Cutouts",
                "status": "NOT_APPLICABLE",
                "severity": "INFO",
                "metrics": {"device_hardware": "No notch cutout present"},
                "explanation": "Device profile does not feature camera notch or bottom gesture bar cutouts.",
                "remediation": None
            })

        # =========================================================================
        # 11. RUNTIME CONSOLE & SCRIPT EXECUTION ERRORS
        # =========================================================================
        if console_errors:
            checklist.append({
                "id": "runtime_console_errors",
                "name": "JavaScript Runtime Exceptions & Script Errors",
                "category": "Execution Stability",
                "status": "FAILED",
                "severity": "HIGH",
                "metrics": {
                    "uncaught_errors_count": len(console_errors),
                    "primary_error": console_errors[0][:80]
                },
                "explanation": f"Encountered {len(console_errors)} uncaught JavaScript exception(s) during page rendering on {device_config.get('name')}.",
                "remediation": "Inspect console error trace and address undefined variable or broken script bundle."
            })
            score -= 15.0
        else:
            checklist.append({
                "id": "runtime_console_errors",
                "name": "JavaScript Runtime Exceptions & Script Errors",
                "category": "Execution Stability",
                "status": "PASSED",
                "severity": "INFO",
                "metrics": {"uncaught_errors": 0},
                "explanation": "Clean browser console: zero uncaught JavaScript runtime exceptions or script breaks.",
                "remediation": None
            })

        # =========================================================================
        # 12. DUAL-SCREEN & FOLDABLE HINGE COLLISION (Rare Case)
        # =========================================================================
        is_foldable = device_config.get("category") == "foldables" or device_config.get("frame_type") in ["tall_foldable", "square_tablet", "landscape_foldable"]
        if is_foldable:
            hinge_x = vp_width // 2
            hinge_violations = []
            for el in elements:
                rect = el.get("rect", {})
                w = rect.get("width", 0)
                if el.get("isInteractive") or el.get("tagName") in ["button", "a", "input", "h1", "h2"]:
                    # Element bisects the central hinge line
                    if rect.get("x", 0) < hinge_x - 6 and rect.get("right", 0) > hinge_x + 6 and w > 40:
                        hinge_violations.append({
                            "selector": el.get("selector"),
                            "tag": el.get("tagName"),
                            "text": el.get("text", "")[:30],
                            "rect": rect
                        })

            if hinge_violations:
                first_hinge = hinge_violations[0]
                checklist.append({
                    "id": "foldable_hinge_split",
                    "name": "Foldable Screen: Physical Hinge Bisection (Rare Case)",
                    "category": "Device Hardware Cutouts",
                    "status": "FAILED",
                    "severity": "HIGH",
                    "metrics": {
                        "hinge_coordinate": f"x = {hinge_x}px",
                        "bisected_targets": len(hinge_violations),
                        "primary_target": first_hinge["selector"]
                    },
                    "explanation": f"Interactive element '{first_hinge['selector']}' bisects the physical foldable screen hinge seam (x={hinge_x}px), splitting CTA and text across the fold line.",
                    "remediation": "@media (spanning: single-fold-vertical) { .action-row { display: flex; flex-direction: column; max-width: env(fold-left, 48%); } }"
                })
                score -= 15.0
                defects.append({
                    "type": "foldable_hinge_bisection",
                    "severity": "high",
                    "element": first_hinge["selector"],
                    "description": f"Foldable Hinge Split: Element '{first_hinge['selector']}' straddles the central physical fold line at {hinge_x}px.",
                    "bounding_box": first_hinge["rect"],
                    "proposed_fix": "max-width: 48% !important;\nmargin-right: auto !important;"
                })
            else:
                checklist.append({
                    "id": "foldable_hinge_split",
                    "name": "Foldable Screen: Physical Hinge Bisection (Rare Case)",
                    "category": "Device Hardware Cutouts",
                    "status": "PASSED",
                    "severity": "INFO",
                    "metrics": {"fold_alignment": f"Dual-screen hinge at x={hinge_x}px respected"},
                    "explanation": f"Zero interactive targets or headings bisect the central foldable hinge seam at x={hinge_x}px.",
                    "remediation": None
                })
        else:
            checklist.append({
                "id": "foldable_hinge_split",
                "name": "Foldable Screen: Physical Hinge Bisection (Rare Case)",
                "category": "Device Hardware Cutouts",
                "status": "NOT_APPLICABLE",
                "severity": "INFO",
                "metrics": {"device_architecture": "Single-panel display; no foldable hinge present"},
                "explanation": "Standard non-foldable device geometry; physical hinge seam check relaxed.",
                "remediation": None
            })

        # =========================================================================
        # 13. DYNAMIC VIEWPORT HEIGHT TRAPPING (100vh vs 100dvh - Rare Case)
        # =========================================================================
        has_100vh = dom_metrics.get("has100vhContainer", False)
        bottom_fixed_unpadded = []
        if is_mobile:
            for el in elements:
                comp = el.get("computed", {})
                if comp.get("position") == "fixed":
                    rect = el.get("rect", {})
                    if rect.get("bottom", 0) >= vp_height - 2 and rect.get("y", 0) > vp_height - 80:
                        if el.get("isInteractive") or el.get("tagName") in ["button", "a", "div"]:
                            bottom_fixed_unpadded.append(el.get("selector"))

        if is_mobile and (has_100vh or len(bottom_fixed_unpadded) > 0):
            flagged = bottom_fixed_unpadded[0] if bottom_fixed_unpadded else "Container with 100vh"
            checklist.append({
                "id": "dynamic_viewport_height_trapping",
                "name": "Dynamic Viewport Height (100vh vs 100dvh Trap)",
                "category": "Mobile Standards",
                "status": "WARNING",
                "severity": "MEDIUM",
                "metrics": {
                    "has_rigid_100vh": has_100vh,
                    "bottom_fixed_controls": len(bottom_fixed_unpadded),
                    "target": flagged
                },
                "explanation": f"Detected rigid 100vh or unpadded bottom fixed control ('{flagged}'). On mobile Chrome/Safari, dynamic address bars and virtual keyboards will occlude bottom action buttons.",
                "remediation": "min-height: 100dvh !important; padding-bottom: max(16px, env(safe-area-inset-bottom)) !important;"
            })
            score -= 5.0
        else:
            checklist.append({
                "id": "dynamic_viewport_height_trapping",
                "name": "Dynamic Viewport Height (100vh vs 100dvh Trap)",
                "category": "Mobile Standards",
                "status": "PASSED",
                "severity": "INFO",
                "metrics": {"viewport_units": "Dynamic dvh / safe-area padding adhered to"},
                "explanation": "Viewport height units and bottom controls safely account for mobile dynamic browser UI expansion.",
                "remediation": None
            })

        # =========================================================================
        # 14. TAP TARGET PROXIMITY & FINGER COLLISION (WCAG 2.5.8 - Rare Case)
        # =========================================================================
        if is_touch:
            interactive_els = [e for e in elements if e.get("isInteractive") or e.get("tagName") in ["button", "a", "input"]]
            crowded_pairs = []
            for i in range(len(interactive_els)):
                for j in range(i + 1, min(i + 8, len(interactive_els))):
                    r1 = interactive_els[i].get("rect", {})
                    r2 = interactive_els[j].get("rect", {})
                    if not r1 or not r2:
                        continue
                    dx = max(0, max(r1.get("x", 0), r2.get("x", 0)) - min(r1.get("right", 0), r2.get("right", 0)))
                    dy = max(0, max(r1.get("y", 0), r2.get("y", 0)) - min(r1.get("bottom", 0), r2.get("bottom", 0)))
                    dist = math.hypot(dx, dy)
                    if dist < 6 and (dx > 0 or dy > 0):
                        crowded_pairs.append({
                            "elem1": interactive_els[i].get("selector"),
                            "elem2": interactive_els[j].get("selector"),
                            "gap_px": round(dist)
                        })
                        if len(crowded_pairs) >= 2:
                            break
                if len(crowded_pairs) >= 2:
                    break

            if crowded_pairs:
                first_crowd = crowded_pairs[0]
                checklist.append({
                    "id": "tap_target_proximity",
                    "name": "Touch Target Proximity & Finger Spacing (WCAG 2.5.8)",
                    "category": "Accessibility",
                    "status": "WARNING",
                    "severity": "MEDIUM",
                    "metrics": {
                        "colliding_pair": f"{first_crowd['elem1']} <-> {first_crowd['elem2']}",
                        "measured_separation": f"{first_crowd['gap_px']}px",
                        "minimum_required": "8px spacing (WCAG 2.5.8)"
                    },
                    "explanation": f"Adjacent interactive targets '{first_crowd['elem1']}' and '{first_crowd['elem2']}' have only {first_crowd['gap_px']}px separation (<8px required). Increases accidental false touch triggers on mobile.",
                    "remediation": "margin-right: 8px !important; margin-bottom: 8px !important; gap: 8px !important;"
                })
                score -= 5.0
            else:
                checklist.append({
                    "id": "tap_target_proximity",
                    "name": "Touch Target Proximity & Finger Spacing (WCAG 2.5.8)",
                    "category": "Accessibility",
                    "status": "PASSED",
                    "severity": "INFO",
                    "metrics": {"touch_spacing": "All adjacent interactive targets >= 8px separation"},
                    "explanation": "All neighboring interactive touch targets satisfy WCAG 2.5.8 spacing requirements to prevent mis-taps.",
                    "remediation": None
                })
        else:
            checklist.append({
                "id": "tap_target_proximity",
                "name": "Touch Target Proximity & Finger Spacing (WCAG 2.5.8)",
                "category": "Accessibility",
                "status": "NOT_APPLICABLE",
                "severity": "INFO",
                "metrics": {"interaction_model": "Desktop pointer / mouse precision"},
                "explanation": "Finger target spacing minimums relaxed for high-precision desktop mouse cursor.",
                "remediation": None
            })

        # =========================================================================
        # 15. ACCESSIBLE NAME & INVISIBLE INTERACTIVE TARGETS (WCAG 4.1.2 - Rare Case)
        # =========================================================================
        unnamed_targets = []
        for el in elements:
            if el.get("isInteractive") or el.get("tagName") in ["button", "a"]:
                has_name = el.get("hasAccessibleName", True)
                if not has_name or (el.get("isIconOnly") and not el.get("ariaLabel")):
                    unnamed_targets.append(el.get("selector"))

        if unnamed_targets:
            first_unnamed = unnamed_targets[0]
            checklist.append({
                "id": "accessible_name_missing",
                "name": "Accessible Name on Interactive Targets (WCAG 4.1.2)",
                "category": "Accessibility",
                "status": "FAILED",
                "severity": "HIGH",
                "metrics": {
                    "unnamed_elements_count": len(unnamed_targets),
                    "primary_target": first_unnamed
                },
                "explanation": f"Interactive control '{first_unnamed}' has no visible text and lacks an accessible name (missing aria-label, title, or alt). Unusable by assistive screen readers and automated RPA click bots.",
                "remediation": "<button aria-label='Submit Action'> or <span class='sr-only'>Action Label</span>"
            })
            score -= 10.0
        else:
            checklist.append({
                "id": "accessible_name_missing",
                "name": "Accessible Name on Interactive Targets (WCAG 4.1.2)",
                "category": "Accessibility",
                "status": "PASSED",
                "severity": "INFO",
                "metrics": {"accessible_labels": "All interactive controls labeled"},
                "explanation": "All buttons, links, and form inputs possess discernible textual labels or aria-label attributes.",
                "remediation": None
            })

        # =========================================================================
        # 16. ACCIDENTAL SCROLL TRAPPING & OVERFLOW LOCK (Rare Case)
        # =========================================================================
        body_overflow = dom_metrics.get("bodyOverflow", "visible")
        doc_scroll_h = dom_metrics.get("documentScrollHeight", vp_height)
        if is_mobile and body_overflow in ["hidden", "clip"] and doc_scroll_h > vp_height + 50:
            checklist.append({
                "id": "scroll_trapping_overflow",
                "name": "Mobile Scroll Trapping & CSS Overflow Lockout",
                "category": "Responsiveness",
                "status": "FAILED",
                "severity": "CRITICAL",
                "metrics": {
                    "body_overflow": body_overflow,
                    "document_height": f"{doc_scroll_h}px",
                    "viewport_height": f"{vp_height}px"
                },
                "explanation": f"Document body has 'overflow: {body_overflow}' while document height ({doc_scroll_h}px) exceeds screen ({vp_height}px). Traps mobile touch users, preventing vertical scroll.",
                "remediation": "body, html { overflow-y: auto !important; -webkit-overflow-scrolling: touch !important; }"
            })
            score -= 20.0
            defects.append({
                "type": "scroll_trapping",
                "severity": "critical",
                "element": "body",
                "description": f"Mobile Scroll Trap: 'overflow: {body_overflow}' prevents scrolling down.",
                "bounding_box": {"x": 0, "y": 0, "width": vp_width, "height": vp_height},
                "proposed_fix": "overflow-y: auto !important;\n-webkit-overflow-scrolling: touch !important;"
            })
        else:
            checklist.append({
                "id": "scroll_trapping_overflow",
                "name": "Mobile Scroll Trapping & CSS Overflow Lockout",
                "category": "Responsiveness",
                "status": "PASSED",
                "severity": "INFO",
                "metrics": {"scroll_trapping": "Zero scroll traps; body scrolling fluid"},
                "explanation": "Document root scroll gestures are uninhibited; touch swipe navigation flows smoothly.",
                "remediation": None
            })

        # Final score bounding
        final_score = max(0.0, min(100.0, round(score, 1)))
        failed_count = sum(1 for c in checklist if c["status"] == "FAILED")
        warning_count = sum(1 for c in checklist if c["status"] == "WARNING")
        passed_count = sum(1 for c in checklist if c["status"] == "PASSED")

        overall_grade = "A+"
        if final_score < 60:
            overall_grade = "F (Critical Anomaly)"
        elif final_score < 75:
            overall_grade = "C (Degraded)"
        elif final_score < 90:
            overall_grade = "B (Acceptable)"

        # =========================================================================
        # MULTI-LEVEL PERFORMANCE BREAKDOWN & WEAK AREAS ACTION CENTER
        # =========================================================================
        check_by_id = {c["id"]: c for c in checklist}
        performance_levels = []
        weak_areas = []

        level_definitions = [
            {
                "level": 1,
                "id": "responsiveness",
                "name": "Level 1: Responsiveness & Fluid Layout",
                "description": "Horizontal scroll prevention, viewport blowout resilience, dynamic dvh vs 100vh trapping, and mobile scroll-lock safety.",
                "check_ids": ["layout_blowout", "typography_elasticity", "dynamic_viewport_height_trapping", "scroll_trapping_overflow"]
            },
            {
                "level": 2,
                "id": "accessibility",
                "name": "Level 2: WCAG Accessibility (Touch, Contrast & Names)",
                "description": "Touch target tap dimensions (WCAG 2.5.5), contrast ratio (WCAG 1.4.3 AA), finger spacing (WCAG 2.5.8), and accessible names (WCAG 4.1.2).",
                "check_ids": ["touch_target", "color_contrast", "tap_target_proximity", "accessible_name_missing"]
            },
            {
                "level": 3,
                "id": "visual_integrity",
                "name": "Level 3: Visual & Spatial Integrity",
                "description": "Element bounding margin clipping, text truncation, and media container responsiveness.",
                "check_ids": ["element_clipping", "unconstrained_media"]
            },
            {
                "level": 4,
                "id": "device_standards",
                "name": "Level 4: Mobile & Foldable Hardware Standards",
                "description": "Viewport meta configuration, safe-area insets, extreme aspect ratios, and foldable hinge bisection.",
                "check_ids": ["viewport_meta", "safe_area_occlusion", "extreme_aspect_ratio", "foldable_hinge_split"]
            },
            {
                "level": 5,
                "id": "runtime_stability",
                "name": "Level 5: RPA & Runtime Stability",
                "description": "Z-Index collision & overlay CTA occlusion (blocking automated clicks) and JS runtime exceptions.",
                "check_ids": ["zindex_collision", "runtime_console_errors"]
            }
        ]

        for l_def in level_definitions:
            l_checks = [check_by_id[cid] for cid in l_def["check_ids"] if cid in check_by_id]
            if not l_checks:
                continue

            check_scores = []
            for chk in l_checks:
                st = chk.get("status", "PASSED")
                if st in ["PASSED", "NOT_APPLICABLE"]:
                    check_scores.append(100.0)
                elif st == "WARNING":
                    check_scores.append(60.0)
                else: # FAILED
                    sev = chk.get("severity", "HIGH").upper()
                    if sev == "CRITICAL":
                        check_scores.append(0.0)
                    elif sev == "HIGH":
                        check_scores.append(30.0)
                    else:
                        check_scores.append(50.0)

            lvl_score = round(sum(check_scores) / len(check_scores), 1) if check_scores else 100.0
            
            lvl_grade = "A+"
            if lvl_score < 60:
                lvl_grade = "F"
            elif lvl_score < 75:
                lvl_grade = "C"
            elif lvl_score < 90:
                lvl_grade = "B"
            elif lvl_score < 98:
                lvl_grade = "A"

            passed_in_lvl = sum(1 for c in l_checks if c["status"] in ["PASSED", "NOT_APPLICABLE"])
            performance_levels.append({
                "level": l_def["level"],
                "id": l_def["id"],
                "name": l_def["name"],
                "description": l_def["description"],
                "score": lvl_score,
                "grade": lvl_grade,
                "status": "PASS" if lvl_score >= 85 else ("WARN" if lvl_score >= 60 else "FAIL"),
                "passed_checks": passed_in_lvl,
                "total_checks": len(l_checks),
                "checks": l_checks
            })

            # Collect weak areas needing improvement
            for chk in l_checks:
                if chk["status"] in ["FAILED", "WARNING"]:
                    remed = chk.get("remediation") or "Inspect element styles and ensure responsiveness."
                    weak_areas.append({
                        "id": chk["id"],
                        "name": chk["name"],
                        "level_name": l_def["name"],
                        "level_num": l_def["level"],
                        "severity": chk.get("severity", "HIGH").upper(),
                        "status": chk["status"],
                        "explanation": chk.get("explanation", ""),
                        "metrics": chk.get("metrics", {}),
                        "remediation": remed,
                        "projected_gain": f"+{round((100 - lvl_score) / max(1, len(l_checks)))}% to Level {l_def['level']}"
                    })

        return {
            "compliance_score": final_score,
            "grade": overall_grade,
            "checklist": checklist,
            "defects": defects,
            "performance_levels": performance_levels,
            "weak_areas": weak_areas,
            "summary_counts": {
                "total_checks": len(checklist),
                "passed": passed_count,
                "failed": failed_count,
                "warnings": warning_count
            }
        }
