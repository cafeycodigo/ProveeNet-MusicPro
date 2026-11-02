(() => {
  const slides = Array.from(document.querySelectorAll('.presentation-slide'));
  if (!slides.length) return;
  const previous = document.getElementById('previous-slide');
  const next = document.getElementById('next-slide');
  const selector = document.getElementById('slide-index');
  const status = document.getElementById('slide-status');
  const progress = document.querySelector('.deck-progress');
  const fromHash = () => {
    const match = location.hash.match(/^#diapositiva-(\d+)$/);
    return match ? Number(match[1]) - 1 : 0;
  };
  let index = 0;
  function show(value, focus = false) {
    index = Math.max(0, Math.min(slides.length - 1, value));
    slides.forEach((slide, n) => { slide.hidden = n !== index; });
    selector.value = String(index);
    status.textContent = `${index + 1} / ${slides.length}`;
    previous.disabled = index === 0;
    next.disabled = index === slides.length - 1;
    progress.value = index + 1;
    history.replaceState(null, '', `#diapositiva-${index + 1}`);
    if (focus) {
      slides[index].focus({preventScroll: true});
      window.scrollTo({top: 0, behavior: 'instant'});
    }
  }
  document.querySelector('.presentation-controls').hidden = false;
  progress.hidden = false;
  previous.addEventListener('click', () => show(index - 1, true));
  next.addEventListener('click', () => show(index + 1, true));
  selector.addEventListener('change', () => show(Number(selector.value), true));
  window.addEventListener('hashchange', () => show(fromHash(), true));
  document.addEventListener('keydown', event => {
    if (event.target.closest('select, input, textarea, button, a, summary') || event.altKey || event.ctrlKey || event.metaKey) return;
    const actions = {ArrowRight: index + 1, PageDown: index + 1, ArrowLeft: index - 1, PageUp: index - 1, Home: 0, End: slides.length - 1};
    if (event.key in actions) { event.preventDefault(); show(actions[event.key], true); }
  });
  const fullscreen = document.getElementById('fullscreen');
  fullscreen.hidden = !document.fullscreenEnabled;
  fullscreen.addEventListener('click', async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch { status.textContent = 'Usa el modo de pantalla completa del navegador.'; }
  });
  document.addEventListener('fullscreenchange', () => { fullscreen.textContent = document.fullscreenElement ? 'Salir de pantalla completa' : 'Pantalla completa'; });
  document.getElementById('print-deck').addEventListener('click', () => window.print());
  show(fromHash());
})();
