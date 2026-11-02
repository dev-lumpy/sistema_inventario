export function navegarA(seccion) {
  const destino = document.getElementById(seccion);
  if (!destino) {
    console.warn(`[router] No existe la sección #${seccion}`);
    return false;
  }

  document.querySelectorAll('.nav-link[data-section]').forEach((link) => {
    link.classList.toggle('active', link.dataset.section === seccion);
  });

  document.querySelectorAll('.content-section').forEach((section) => {
    section.classList.toggle('active', section === destino);
  });

  document.dispatchEvent(new CustomEvent('seccion:activada', { detail: { seccion } }));

  if (window.innerWidth <= 900) {
    document.getElementById('sidebar')?.classList.remove('open');
  }

  return true;
}

export function initRouter() {
  document.addEventListener('click', (evento) => {
    const trigger = evento.target.closest('[data-section]');
    if (!trigger) return;

    if (trigger.matches('a')) evento.preventDefault();
    navegarA(trigger.dataset.section);
  });
}
