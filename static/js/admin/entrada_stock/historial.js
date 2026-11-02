import { $, crearFilaEstado, crearEl } from '../../shared/core/dom.js';
import { formatearFecha } from '../../shared/core/format.js';
import { obtenerHistorial } from './api.js';

function crearFila(entrada) {
  const tr = document.createElement('tr');

  tr.append(
    crearEl('td', { texto: entrada.producto ?? '—' }),
    crearEl('td', { texto: entrada.cantidad }),
    crearEl('td', { texto: entrada.proveedor ?? '—' }),
    crearEl('td', { texto: formatearFecha(entrada.fecha) }),
  );

  return tr;
}

export async function cargarHistorial() {
  const tbody = $('#tbody-entradas');
  if (!tbody) return;

  tbody.replaceChildren();

  try {
    const entradas = await obtenerHistorial();

    if (!entradas.length) {
      tbody.replaceChildren(crearFilaEstado(4, 'No hay entradas registradas.', {
        icono: 'fa-inbox',
      }));
      return;
    }

    tbody.replaceChildren(...entradas.map(crearFila));
  } catch (error) {
    tbody.replaceChildren(crearFilaEstado(4, `Error al cargar el historial: ${error.message}`, {
      icono: 'fa-triangle-exclamation',
      error: true,
    }));
  }
}
