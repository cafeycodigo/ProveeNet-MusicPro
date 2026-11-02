(() => {
  const demoDialog = document.getElementById('demo-access-dialog');
  const demoOpen = document.getElementById('open-demo-access');
  if (demoDialog && demoOpen) {
    const accounts = JSON.parse(document.getElementById('demo-accounts-data').textContent);
    demoOpen.addEventListener('click', () => { demoDialog.showModal(); document.body.classList.add('demo-modal-open'); });
    demoDialog.addEventListener('close', () => document.body.classList.remove('demo-modal-open'));
    document.getElementById('close-demo-access').addEventListener('click', () => demoDialog.close());
    demoDialog.addEventListener('click', event => {
      const rect = demoDialog.getBoundingClientRect();
      if (event.target === demoDialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) demoDialog.close();
    });
    demoDialog.querySelectorAll('[data-demo-account]').forEach(button => button.addEventListener('click', () => {
      const account = accounts[Number(button.dataset.demoAccount)];
      if (!account) return;
      const username = document.getElementById('id_username');
      const password = document.getElementById('id_password');
      username.value = account.email || account.username;
      password.value = account.password;
      password.type = 'password';
      const toggle = document.querySelector('[data-password-toggle]');
      if (toggle) { toggle.textContent = 'Mostrar'; toggle.setAttribute('aria-pressed', 'false'); }
      for (const input of [username, password]) {
        input.dispatchEvent(new Event('input', {bubbles: true}));
        input.dispatchEvent(new Event('change', {bubbles: true}));
      }
      demoDialog.close();
      document.getElementById('demo-fill-status').textContent = `${account.title}: datos completados. Pulsa Iniciar sesión.`;
      document.querySelector('[data-loading-label]').focus({preventScroll: true});
    }));
  }
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
