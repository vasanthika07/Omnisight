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
                        selector: el.id ? `#${el.id}` : (el.className ? `.${el.className.split(' ').join('.')}` : sel),
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
                            maxWidth: computed.maxWidth,
                            boxSizing: computed.boxSizing,
                            overflow: computed.overflow,
                            display: computed.display,
                            position: computed.position
                        },
                        overflowsViewport: overflowsRight || overflowsLeft,
                        overflowPixels: overflowsRight ? Math.round(rect.right - viewportWidth) : 0
                    });
                }
            });
        });
        
        return {
            viewport: { width: viewportWidth, height: viewportHeight },
            documentScrollWidth: document.documentElement.scrollWidth,
            hasHorizontalScrollbar: document.documentElement.scrollWidth > viewportWidth,
            elements: elementsInfo
        };
    }""")
    
    return metrics
