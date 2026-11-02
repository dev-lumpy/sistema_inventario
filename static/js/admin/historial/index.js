import { $ } from '../../shared/core/dom.js';
import { getMovimientos, getProductos } from './api.js';
import { renderProductos } from './productos.js';
import { renderHistorial } from './tabla.js';

export async function initHistorial() {
  const select = $('#historial-producto');
  if (!select) return;

  let productos = [];
  let movimientos = [];

  const aplicarFiltro = () => {
    const productoId = select.value;
    if (!productoId) {
      renderHistorial(movimientos);
      return;
    }

    const producto = productos.find(
      (item) => String(item.id) === String(productoId),
    );

    // El backend expone la categoría del movimiento, no el producto:
    // filtramos por la categoría del producto elegido.
    const filtrados = producto
      ? movimientos.filter((movimiento) => movimiento.categoria === producto.categoria)
      : movimientos;

    renderHistorial(filtrados);
  };

  const cargar = async () => {
    try {
      [productos, movimientos] = await Promise.all([getProductos(), getMovimientos()]);
      renderProductos(productos);
      aplicarFiltro();
    } catch (error) {
      console.error('[historial]', error);
      renderHistorial([], { error: `No se pudo cargar el historial: ${error.message}` });
    }
  };

  select.addEventListener('change', aplicarFiltro);

  document.addEventListener('seccion:activada', (evento) => {
    if (evento.detail.seccion === 'historial') cargar();
  });

  await cargar();
}
