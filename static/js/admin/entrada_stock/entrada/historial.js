// static/js/admin/entrada_stock/js/entrada/historial.js
import { $ } from '../utils/dom.js';
import { formatearFecha } from '../utils/format.js';
import { obtenerHistorial } from '../services/entrada.service.js';

export async function cargarHistorial() {
  const tbody = $('#tbody-entradas');
  if (!tbody) return;

  tbody.replaceChildren();

  try {
    const entradas = await obtenerHistorial();
    if (!entradas.length) {
      const tr = document.createElement('tr');
      const td = document.createElement('td');
      td.colSpan = 4;
      td.textContent = 'No hay entradas registradas.';
      td.className = 'empty-state';
      tr.appendChild(td);
      tbody.appendChild(tr);
      return;
    }

    for (const e of entradas) {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${e.producto}</td>
        <td>${e.cantidad}</td>
        <td>${e.proveedor ?? '—'}</td>
        <td>${formatearFecha(e.fecha)}</td>
      `;
      tbody.appendChild(tr);
    }
  } catch (err) {
    const tr = document.createElement('tr');
    const td = document.createElement('td');
    td.colSpan = 4;
    td.textContent = `Error al cargar el historial: ${err.message}`;
    td.className = 'empty-state';
    tr.appendChild(td);
    tbody.appendChild(tr);
  }
}
