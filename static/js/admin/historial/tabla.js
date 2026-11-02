import { $, crearEl, crearFilaEstado } from '../../shared/core/dom.js';
import { formatearFecha, formatearNumero } from '../../shared/core/format.js';

function crearFila(movimiento) {
  const tr = document.createElement('tr');

  tr.append(
    crearEl('td', { texto: movimiento.categoria ?? '—' }),
    crearEl('td', { texto: formatearNumero(movimiento.cantidad) }),
    crearEl('td', { texto: movimiento.proveedor ?? '—' }),
    crearEl('td', { texto: formatearFecha(movimiento.fecha) }),
  );

  return tr;
}

export function renderHistorial(movimientos, { error = null } = {}) {
  const tbody = $('#tbody-historial');
  const vacio = $('#historial-vacio');
  if (!tbody) return;

  tbody.replaceChildren();

  if (error) {
    tbody.replaceChildren(crearFilaEstado(4, error, {
      icono: 'fa-triangle-exclamation',
      error: true,
    }));
    if (vacio) vacio.hidden = true;
    return;
  }

  const ordenados = [...(movimientos || [])].sort(
    (a, b) => new Date(b.fecha) - new Date(a.fecha),
  );

  if (!ordenados.length) {
    if (vacio) {
      vacio.hidden = false;
      vacio.textContent = 'No hay movimientos para este producto.';
    }
    return;
  }

  if (vacio) vacio.hidden = true;
  tbody.replaceChildren(...ordenados.map(crearFila));
}
