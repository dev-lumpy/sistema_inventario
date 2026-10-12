// static/js/admin/inicio/js/inicio/accesos.js
import { $ } from '../utils/dom.js';
import { navegarA } from '../core/navegacion.js';

/** Un solo listener (delegación) para todos los botones de acciones rápidas. */
export function initAccesos() {
  const contenedor = $('.accesos-rapidos');
  if (!contenedor) return;

  contenedor.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-section]');
    if (btn) navegarA(btn.dataset.section);
  });
}
