from playwright.sync_api import Page
from typing import Dict, Any, List

def extract_dom_and_metrics(page: Page) -> Dict[str, Any]:
    """
    Extracts high-value DOM structure, computed CSS properties, and bounding boxes
    of interactive and critical elements for multimodal visual-spatial correlation.
    Supports local apps as well as arbitrary external websites.
    """
    metrics = page.evaluate("""() => {
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        function getSafeSelector(el) {
            if (el.id && /^[a-zA-Z][a-zA-Z0-9_-]*$/.test(el.id)) {
                return `#${el.id}`;
            }
            const tag = el.tagName.toLowerCase();
            if (el.className && typeof el.className === 'string') {
                const classes = el.className.split(/\\s+/).filter(c => /^[a-zA-Z][a-zA-Z0-9_-]*$/.test(c) && !c.includes(':'));
                if (classes.length > 0) {
                    return `${tag}.${classes.slice(0, 2).join('.')}`;
                }
            }
            if (el.getAttribute('data-testid')) {
                return `[data-testid="${el.getAttribute('data-testid')}"]`;
            }
            if (el.getAttribute('name')) {
                return `${tag}[name="${el.getAttribute('name')}"]`;
            }
            if (el.parentElement) {
                const parentTag = el.parentElement.tagName.toLowerCase();
                const siblings = Array.from(el.parentElement.children);
                const index = siblings.indexOf(el) + 1;
                return `${parentTag} > ${tag}:nth-child(${index})`;
            }
            return tag;
        }

        // Find critical interactive and layout elements across both local and external sites
        const candidateSelectors = [
            'button', 'a', 'input', 'select', 'textarea', '[role="button"]',
            'header', 'nav', 'main', 'aside', 'footer', 'article', 'section',
            'h1', 'h2', 'h3', 'table', 'form', 'img',
            '.checkout-action-btn', '#checkout-btn', '.summary-card', '.card',
            '.btn', '.button', '.cta', '.banner', '.hero'
        ];
        
        const elementsInfo = [];
        const visitedElements = new Set();
        
        candidateSelectors.forEach(sel => {
            try {
                const els = document.querySelectorAll(sel);
                els.forEach(el => {
                    if (visitedElements.has(el)) return;
                    visitedElements.add(el);
                    
                    const rect = el.getBoundingClientRect();
                    const computed = window.getComputedStyle(el);
                    
                    // Check if element is visible
                    const isVisible = rect.width > 0 && rect.height > 0 && 
                                      computed.display !== 'none' && 
                                      computed.visibility !== 'hidden' && 
                                      computed.opacity !== '0';
                    
                    if (isVisible) {
                        // Check horizontal overflow relative to viewport
                        const overflowsRight = rect.right > viewportWidth + 3;
                        const overflowsLeft = rect.left < -3;
                        const overflowsWidth = rect.width > viewportWidth + 3;
                        
                        elementsInfo.push({
                            selector: getSafeSelector(el),
                            tagName: el.tagName.toLowerCase(),
                            id: el.id || null,
                            className: typeof el.className === 'string' ? el.className : null,
                            text: (el.innerText || el.textContent || '').trim().slice(0, 80),
                            rect: {
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height),
                                right: Math.round(rect.right),
                                bottom: Math.round(rect.bottom)
                            },
                            computed: {
                                width: computed.width,
                                height: computed.height,
                                maxWidth: computed.maxWidth,
                                boxSizing: computed.boxSizing,
                                overflow: computed.overflow,
                                display: computed.display,
                                position: computed.position,
                                zIndex: computed.zIndex,
                                color: computed.color,
                                backgroundColor: computed.backgroundColor,
                                fontSize: computed.fontSize
                            },
                            isTouchTargetSmall: (el.tagName === 'BUTTON' || el.tagName === 'A' || (el.className && typeof el.className === 'string' && el.className.includes('btn'))) && (rect.width < 44 || rect.height < 44),
                            overflowsViewport: overflowsRight || overflowsLeft || overflowsWidth,
                            overflowPixels: Math.round(Math.max(0, rect.right - viewportWidth, rect.width - viewportWidth))
                        });
                    }
                });
            } catch (e) {
                // Ignore invalid query selector if any
            }
        });

        // Scan all visible elements specifically for horizontal overflow anomalies
        try {
            const allElements = document.querySelectorAll('body *');
            for (let i = 0; i < allElements.length && elementsInfo.length < 80; i++) {
                const el = allElements[i];
                if (visitedElements.has(el)) continue;
                const rect = el.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    if (rect.right > viewportWidth + 4 || rect.width > viewportWidth + 4 || rect.left < -4) {
                        visitedElements.add(el);
                        const computed = window.getComputedStyle(el);
                        elementsInfo.push({
                            selector: getSafeSelector(el),
                            tagName: el.tagName.toLowerCase(),
                            id: el.id || null,
                            className: typeof el.className === 'string' ? el.className : null,
                            text: (el.innerText || el.textContent || '').trim().slice(0, 80),
                            rect: {
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height),
                                right: Math.round(rect.right),
                                bottom: Math.round(rect.bottom)
                            },
                            computed: {
                                width: computed.width,
                                height: computed.height,
                                maxWidth: computed.maxWidth,
                                boxSizing: computed.boxSizing,
                                overflow: computed.overflow,
                                display: computed.display,
                                position: computed.position,
                                zIndex: computed.zIndex,
                                color: computed.color,
                                backgroundColor: computed.backgroundColor,
                                fontSize: computed.fontSize
                            },
                            isTouchTargetSmall: (el.tagName === 'BUTTON' || el.tagName === 'A') && (rect.width < 44 || rect.height < 44),
                            overflowsViewport: true,
                            overflowPixels: Math.round(Math.max(0, rect.right - viewportWidth, rect.width - viewportWidth))
                        });
                    }
                }
            }
        } catch (e) {}

        // Detect overlapping elements (e.g. floating promo banner obscuring button)
        // Detect overlapping elements (e.g. floating promo banner obscuring button)
        const overlaps = [];
        for (let i = 0; i < elementsInfo.length; i++) {
            for (let j = i + 1; j < elementsInfo.length; j++) {
                const a = elementsInfo[i];
                const b = elementsInfo[j];
                if (!a.rect || !b.rect) continue;
                // Exclude normal document-flow parent/child containment; require at least one floating/overlay element
                const isFloatingA = a.computed.position === 'absolute' || a.computed.position === 'fixed' || (a.className && typeof a.className === 'string' && a.className.includes('overlay'));
                const isFloatingB = b.computed.position === 'absolute' || b.computed.position === 'fixed' || (b.className && typeof b.className === 'string' && b.className.includes('overlay'));
                if (!isFloatingA && !isFloatingB) continue;

                const xOverlap = Math.max(0, Math.min(a.rect.right, b.rect.right) - Math.max(a.rect.x, b.rect.x));
                const yOverlap = Math.max(0, Math.min(a.rect.bottom, b.rect.bottom) - Math.max(a.rect.y, b.rect.y));
                const overlapArea = xOverlap * yOverlap;

                // If collision is significant and one is an interactive button/input
                if (overlapArea > 200 && (a.tagName === 'button' || b.tagName === 'button' || a.selector.includes('btn') || b.selector.includes('btn'))) {
                    overlaps.push({
                        elementA: a.selector,
                        elementB: b.selector,
                        overlapArea: Math.round(overlapArea),
                        overlapRect: {
                            x: Math.max(a.rect.x, b.rect.x),
                            y: Math.max(a.rect.y, b.rect.y),
                            width: xOverlap,
                            height: yOverlap
                        }
                    });
                }
            }
        }

        // Viewport Meta Tag Audit
        const vpMetaEl = document.querySelector('meta[name="viewport"]');
        let metaInfo = {
            hasViewportMeta: !!vpMetaEl,
            content: vpMetaEl ? vpMetaEl.getAttribute('content') : '',
            userScalable: true,
            initialScale: "1.0"
        };
        if (vpMetaEl && vpMetaEl.getAttribute('content')) {
            const contentStr = vpMetaEl.getAttribute('content').toLowerCase();
            metaInfo.userScalable = !contentStr.includes('user-scalable=no') && !contentStr.includes('maximum-scale=1.0');
            const matchScale = contentStr.match(/initial-scale=([0-9.]+)/);
            if (matchScale) metaInfo.initialScale = matchScale[1];
        }

        // Media items audit
        const mediaItems = [];
        try {
            const imgs = document.querySelectorAll('img');
            imgs.forEach((img, idx) => {
                if (idx < 25) {
                    const r = img.getBoundingClientRect();
                    const comp = window.getComputedStyle(img);
                    const isBroken = img.complete && img.naturalWidth === 0 && img.src && !img.src.startsWith('data:');
                    mediaItems.push({
                        src: (img.src || '').slice(0, 100),
                        width: Math.round(r.width),
                        height: Math.round(r.height),
                        naturalWidth: img.naturalWidth || 0,
                        naturalHeight: img.naturalHeight || 0,
                        isBroken: isBroken,
                        hasFluidConstraint: comp.maxWidth !== 'none' || comp.width === '100%'
                    });
                }
            });
        } catch (e) {}

        // Sticky Elements Total Height (for mobile landscape check)
        let stickyHeight = 0;
        try {
            const fixedEls = document.querySelectorAll('header, nav, [style*="position: fixed"], [style*="position: sticky"]');
            fixedEls.forEach(el => {
                const r = el.getBoundingClientRect();
                const comp = window.getComputedStyle(el);
                if ((comp.position === 'fixed' || comp.position === 'sticky') && r.top < 30 && r.height > 20) {
                    stickyHeight += r.height;
                }
            });
        } catch (e) {}

        // Container max width for ultrawide check
        const mainEl = document.querySelector('main, .checkout-wrapper, .container, #root, #app') || document.body;
        const mainComp = window.getComputedStyle(mainEl);
        const bodyMaxWidth = mainComp.maxWidth || 'none';
        
        return {
            viewport: { width: viewportWidth, height: viewportHeight },
            documentScrollWidth: document.documentElement.scrollWidth,
            hasHorizontalScrollbar: document.documentElement.scrollWidth > viewportWidth + 3,
            pageTitle: document.title || window.location.hostname || 'Target Page',
            currentUrl: window.location.href,
            elements: elementsInfo,
            overlaps: overlaps,
            meta_info: metaInfo,
            media_items: mediaItems,
            stickyElementsTotalHeight: Math.round(stickyHeight),
            bodyMaxWidth: bodyMaxWidth
        };
    }""")
    
    return metrics
