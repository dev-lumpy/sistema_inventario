// static/js/admin/entrada_stock/js/data_historial.js

/**
 * Renderiza la tabla de movimientos de stock en <tbody id="tbody-historial">.
 * Recibe la lista de movimientos ya cargada (por main.js).
 *
 * @param {Array<{
 *   id: number,
 *   categoria: string,
 *   cantidad: number,
 *   proveedor: string,
 *   fecha: string,
 * }>} movimientos
 */
export function renderHistorialTabla(movimientos) {
  const tbody = document.getElementById('tbody-historial');
  const vacio = document.getElementById('historial-vacio');
  if (!tbody) return;

  // Limpiar
  tbody.replaceChildren();

  const lista = movimientos || [];

  // Estado vacío
  if (!lista.length) {
    if (vacio) {
      vacio.hidden = false;
      vacio.textContent = 'No hay movimientos registrados.';
    }
    return;
  }
  if (vacio) vacio.hidden = true;

  // Ordenar de más reciente a más antiguo
  const ordenados = [...lista].sort(
    (a, b) => new Date(b.fecha) - new Date(a.fecha),
  );

  for (const m of ordenados) {
    const tr = document.createElement('tr');

    tr.innerHTML = `
      <td>${escaparHtml(m.categoria)}</td>
      <td>${formatearNumero(m.cantidad)}</td>
      <td>${escaparHtml(m.proveedor)}</td>
      <td>${formatearFecha(m.fecha)}</td>
    `;

    tbody.appendChild(tr);
  }
}


/* ---------- Helpers locales ---------- */

function escaparHtml(str) {
  if (str == null) return '';
  return String(str)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

function formatearNumero(n) {
  return Number(n).toLocaleString('es-AR');
}

function formatearFecha(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleString('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}
