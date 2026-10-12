 // static/js/admin/entrada_stock/js/entrada/formulario.js
import { $, limpiarSelect, llenarSelect, mostrarMensaje, ocultarMensaje } from '../utils/dom.js';
import { obtenerProductos, obtenerProveedores, registrarEntrada } from '../services/entrada.service.js';

export async function initFormulario() {
  const form = $('#form-registrar-entrada');
  const selectProducto = $('#entrada-producto');
  const selectProveedor = $('#entrada-proveedor');
  const inputCantidad = $('#entrada-cantidad');
  const mensaje = $('#entrada-mensaje');

  // Cargar selects
  try {
    const [productos, proveedores] = await Promise.all([
      obtenerProductos(),
      obtenerProveedores(),
    ]);

    limpiarSelect(selectProducto, 'Seleccioná un producto');
    llenarSelect(selectProducto, productos);

    limpiarSelect(selectProveedor, 'Seleccioná un proveedor');
    llenarSelect(selectProveedor, proveedores);
  } catch (err) {
    mostrarMensaje(mensaje, `No se pudieron cargar los datos: ${err.message}`, 'error');
    return;
  }

  // Submit
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    ocultarMensaje(mensaje);

    const producto_id = selectProducto.value;
    const proveedor_id = selectProveedor.value;
    const cantidad = Number(inputCantidad.value);

    if (!producto_id) return mostrarMensaje(mensaje, 'Elegí un producto.', 'error');
    if (!cantidad || cantidad < 1) return mostrarMensaje(mensaje, 'La cantidad debe ser mayor a cero.', 'error');
    if (!proveedor_id) return mostrarMensaje(mensaje, 'Elegí un proveedor.', 'error');

    const boton = form.querySelector('button[type="submit"]');
    boton.disabled = true;

    try {
      const res = await registrarEntrada({ producto_id, cantidad, proveedor_id });
      mostrarMensaje(
        mensaje,
        `Entrada registrada. Nuevo stock: ${res.nuevo_stock}.`,
        'exito',
      );
      form.reset();
    } catch (err) {
      mostrarMensaje(mensaje, err.message, 'error');
    } finally {
      boton.disabled = false;
    }
  });
}
