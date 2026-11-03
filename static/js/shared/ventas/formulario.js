import { $, limpiarSelect, llenarSelect, mostrarMensaje, ocultarMensaje } from '../core/dom.js';
import { obtenerProductos, addMovimientoStock } from './api.js';

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
  const inputCantidad = $('#venta-cantidad');
  const selectCanal = $('#venta-canal');
  const ayudaStock = $('#venta-producto-stock');
  const mensaje = $('#venta-mensaje');
  const boton = form.querySelector('button[type="submit"]');

  let productos = [];

  try {
    productos = aLista(await obtenerProductos());
    limpiarSelect(selectProducto, 'Seleccioná un producto');
    llenarSelect(selectProducto, productos);
  } catch (error) {
    mostrarMensaje(mensaje, `No se pudieron cargar los productos: ${error.message}`, 'error');
    return;
  }

  const productoSeleccionado = () => productos.find(
    (p) => String(p.id) === selectProducto.value,
  );

  selectProducto.addEventListener('change', () => {
    if (!ayudaStock) return;
    const producto = productoSeleccionado();
    ayudaStock.textContent = producto
      ? `Stock disponible: ${producto.stock_actual ?? '—'}`
      : 'Stock disponible: —';
  });

  form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    ocultarMensaje(mensaje);

    const producto_id = selectProducto.value;
    const cantidad = Number(inputCantidad.value);
    const canal_venta = selectCanal.value;

    if (!producto_id) return mostrarMensaje(mensaje, 'Elegí un producto.', 'error');
    if (!cantidad || cantidad < 1) return mostrarMensaje(mensaje, 'La cantidad debe ser mayor a cero.', 'error');
    if (!canal_venta) return mostrarMensaje(mensaje, 'Elegí un canal de venta.', 'error');

    const producto = productoSeleccionado();
    if (producto && cantidad > Number(producto.stock_actual ?? 0)) {
      return mostrarMensaje(mensaje, `No hay stock suficiente. Disponible: ${producto.stock_actual}.`, 'error');
    }

    if (boton) boton.disabled = true;

    try {
      const respuesta = await addMovimientoStock({
        producto: Number(producto_id),
        cantidad,
        canal_venta,
      });

      if (producto) producto.stock_actual = respuesta.nuevo_stock;

      mostrarMensaje(mensaje, `Venta registrada. Nuevo stock: ${respuesta.nuevo_stock}.`, 'exito');
      form.reset();
      if (ayudaStock) ayudaStock.textContent = 'Stock disponible: —';
    } catch (error) {
      mostrarMensaje(mensaje, error.message, 'error');
    } finally {
      if (boton) boton.disabled = false;
    }
  });
}
