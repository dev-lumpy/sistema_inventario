// static/js/admin/inicio/js/core/navegacion.js
/**
 * Navegación entre secciones.
 * Dispara el evento cancelable "navegar". Si tu router/sidebar ya escucha
 * ese evento y llama a preventDefault(), se usa el tuyo; si no, se aplica
 * un cambio simple de la clase .active en las .content-section.
 */
export function navegarA(seccion) {
  const evento = new CustomEvent('navegar', {
    detail: { seccion },
    cancelable: true,
  });
  if (!document.dispatchEvent(evento)) return; // alguien más lo manejó

  const destino = document.getElementById(seccion);
  if (!destino) {
    console.warn(`[navegacion] No existe la sección #${seccion}`);
    return;
  }
  document
    .querySelectorAll('.content-section.active')
    .forEach((s) => s.classList.remove('active'));
  destino.classList.add('active');
  document.dispatchEvent(new CustomEvent('seccion:activada', { detail: { seccion } }));
}
