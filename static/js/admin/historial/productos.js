import { $, limpiarSelect, llenarSelect } from '../../shared/core/dom.js';

export function renderProductos(productos) {
  const select = $('#historial-producto');
  if (!select) return;

  const ordenados = [...(productos || [])].sort(
    (a, b) => a.nombre.localeCompare(b.nombre),
  );

  limpiarSelect(select, 'Seleccioná un producto');
  llenarSelect(select, ordenados);
  select.disabled = ordenados.length === 0;
}
