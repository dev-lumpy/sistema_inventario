// static/js/admin/entrada_stock/js/main.js

import { 
    getMovimientosStock,
    getProductos
} from './api.js';

const movimientos = await getMovimientosStock();
const productos = await getProductos();

import { renderHistorialTabla } from './data_historial.js';
import { renderHistorialProductos } from './data_productos.js';

async function init() {
  try {
    renderHistorialProductos(productos);
    renderHistorialTabla(movimientos)
  } catch (err) {
    console.error('[main] Error al inicializar:', err);
  }
}

init();

document.getElementById('historial-producto').addEventListener('change', (e) => {
  const productoId = e.target.value;

  // 1. Buscar el producto elegido
  const productoSeleccionado = productoId
    ? productos.find((p) => String(p.id) === productoId)
    : null;

  // 2. Filtrar movimientos por la categoría del producto
  const movimientosFiltrados = productoSeleccionado
    ? movimientos.filter((m) => m.categoria === productoSeleccionado.categoria)
    : movimientos;

  // 3. Pintar
  renderHistorialTabla(movimientosFiltrados);
});
