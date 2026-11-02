import { $, limpiarSelect, llenarSelect, mostrarMensaje } from '../core/dom.js';
import { obtenerProductos } from './api.js';

function aLista(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

export async function initFormulario() {
  const form = $('#form-registrar-venta');
  if (!form) return;

  const selectProducto = $('#venta-producto');
  const ayudaStock = $('#venta-producto-stock');
  const mensaje = $('#venta-mensaje');

  let productos = [];

  try {
    productos = aLista(await obtenerProductos());
    limpiarSelect(selectProducto, 'Seleccioná un producto');
    llenarSelect(selectProducto, productos);
  } catch (error) {
    mostrarMensaje(mensaje, `No se pudieron cargar los productos: ${error.message}`, 'error');
    return;
  }

  selectProducto.addEventListener('change', () => {
    if (!ayudaStock) return;
    const producto = productos.find((p) => String(p.id) === selectProducto.value);
    ayudaStock.textContent = producto
      ? `Stock disponible: ${producto.stock_actual ?? '—'}`
      : 'Stock disponible: —';
  });
}
