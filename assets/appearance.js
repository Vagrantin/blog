(() => {
  const select = document.getElementById('appearance');
  if (!select) return;
  const valid = value => value === 'light' || value === 'dark';
  function apply(value) {
    if (valid(value)) document.documentElement.dataset.theme = value;
    else delete document.documentElement.dataset.theme;
    select.value = valid(value) ? value : 'system';
  }
  apply(document.documentElement.dataset.theme);
  select.closest('label').hidden = false;
  select.addEventListener('change', () => {
    apply(select.value);
    try {
      if (valid(select.value)) localStorage.setItem('nekkuma-appearance', select.value);
      else localStorage.removeItem('nekkuma-appearance');
    } catch (_) { /* The choice still works for this page. */ }
  });
  window.addEventListener('storage', event => {
    if (event.key === 'nekkuma-appearance' || event.key === null) apply(event.newValue);
  });
})();
