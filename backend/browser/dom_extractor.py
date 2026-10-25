from playwright.sync_api import Page
from typing import Dict, Any, List

def extract_dom_and_metrics(page: Page) -> Dict[str, Any]:
    """
    Extracts high-value DOM structure, computed CSS properties, and bounding boxes
    of interactive and critical elements for multimodal visual-spatial correlation.
    """
    metrics = page.evaluate("""() => {
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        // Find critical interactive and layout elements
        const candidateSelectors = [
            'button', 'a', 'input', 'select', 'header', 'main', 'aside',
            '.checkout-action-btn', '#checkout-btn', '.summary-card', '.card'
        ];
        
        const elementsInfo = [];
        const visitedElements = new Set();
        
        candidateSelectors.forEach(sel => {
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
                    const overflowsRight = rect.right > viewportWidth;
                    const overflowsLeft = rect.left < 0;
                    
                    elementsInfo.push({
                        selector: el.id ? `#${el.id}` : (el.className ? `.${el.className.split(' ').filter(Boolean).join('.')}` : sel),
                        tagName: el.tagName.toLowerCase(),
                        id: el.id || null,
                        className: el.className || null,
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
                        isTouchTargetSmall: (el.tagName === 'BUTTON' || el.tagName === 'A' || el.className.includes('btn')) && (rect.width < 44 || rect.height < 44),
                        overflowsViewport: overflowsRight || overflowsLeft,
                        overflowPixels: overflowsRight ? Math.round(rect.right - viewportWidth) : 0
                    });
                }
            });
        });

        // Detect overlapping elements (e.g. floating promo banner obscuring button)
        const overlaps = [];
        for (let i = 0; i < elementsInfo.length; i++) {
            for (let j = i + 1; j < elementsInfo.length; j++) {
                const a = elementsInfo[i];
                const b = elementsInfo[j];
                if (!a.rect || !b.rect) continue;
                // Exclude normal document-flow parent/child containment; require at least one floating/overlay element
                const isFloatingA = a.computed.position === 'absolute' || a.computed.position === 'fixed' || (a.className && a.className.includes('overlay'));
                const isFloatingB = b.computed.position === 'absolute' || b.computed.position === 'fixed' || (b.className && b.className.includes('overlay'));
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
        
        return {
            viewport: { width: viewportWidth, height: viewportHeight },
            documentScrollWidth: document.documentElement.scrollWidth,
            hasHorizontalScrollbar: document.documentElement.scrollWidth > viewportWidth,
            elements: elementsInfo,
            overlaps: overlaps
        };
    }""")
    
    return metrics
