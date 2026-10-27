// Apply explicit preference before CSS paints. System mode needs no attribute.
try {
  const value = localStorage.getItem('nekkuma-appearance');
  if (value === 'light' || value === 'dark') document.documentElement.dataset.theme = value;
} catch (_) { /* Storage may be disabled; CSS still follows the system. */ }
