// OmniStore Checkout Demo Script
document.addEventListener('DOMContentLoaded', () => {
  const checkoutBtn = document.getElementById('checkout-btn');
  if (checkoutBtn) {
    checkoutBtn.addEventListener('click', () => {
      checkoutBtn.style.transform = 'scale(0.97)';
      setTimeout(() => {
        checkoutBtn.style.transform = '';
        alert('OmniSight Demo: Checkout initiated successfully!');
      }, 150);
    });
  }

  // Detect and log if button is overflowing viewport in console
  const rect = checkoutBtn.getBoundingClientRect();
  const viewportWidth = window.innerWidth;
  if (rect.right > viewportWidth) {
    console.warn(
      `[OmniSight Defect Notice]: Element #checkout-btn overflows viewport by ${(rect.right - viewportWidth).toFixed(1)}px (width: ${rect.width}px, viewport: ${viewportWidth}px)`
    );
  }
});
