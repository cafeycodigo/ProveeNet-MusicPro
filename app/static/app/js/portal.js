(() => {
  const toggle = document.querySelector('[data-password-toggle]');
  if (toggle) toggle.addEventListener('click', () => {
    const input = document.getElementById(toggle.getAttribute('aria-controls'));
    const visible = input.type === 'password';
    input.type = visible ? 'text' : 'password';
    toggle.textContent = visible ? 'Ocultar' : 'Mostrar';
    toggle.setAttribute('aria-pressed', String(visible));
  });
  document.querySelectorAll('[data-loading-form]').forEach(form => form.addEventListener('submit', () => {
    const button = form.querySelector('[data-loading-label]');
    if (button) { button.disabled = true; button.textContent = button.dataset.loadingLabel; button.setAttribute('aria-busy', 'true'); }
  }));
  window.addEventListener('pageshow', event => { if (event.persisted) location.reload(); });
  const menu = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('workspace-sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  if (!menu || !sidebar || !backdrop) return;
  function setOpen(open) {
    document.body.classList.toggle('sidebar-open', open);
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
    backdrop.hidden = !open;
  }
  menu.addEventListener('click', () => setOpen(menu.getAttribute('aria-expanded') !== 'true'));
  backdrop.addEventListener('click', () => setOpen(false));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') { setOpen(false); menu.focus(); }
  });
  const media = matchMedia('(max-width: 1023px)');
  function syncSidebar() {
    const closed = media.matches && menu.getAttribute('aria-expanded') !== 'true';
    sidebar.inert = closed;
  }
  menu.addEventListener('click', syncSidebar);
  backdrop.addEventListener('click', syncSidebar);
  document.addEventListener('keydown', event => { if (event.key === 'Escape') syncSidebar(); });
  media.addEventListener('change', () => { setOpen(false); syncSidebar(); });
  syncSidebar();
})();
