import { $, limpiarSelect, llenarSelect, mostrarMensaje, ocultarMensaje } from '../../shared/core/dom.js';
import { obtenerProductos, obtenerProveedores, registrarEntrada } from './api.js';

export async function cargarCombos() {
  const selectProducto = $('#entrada-producto');
  const selectProveedor = $('#entrada-proveedor');
  if (!selectProducto || !selectProveedor) return;

  const [productos, proveedores] = await Promise.all([
    obtenerProductos(),
    obtenerProveedores(),
  ]);

  limpiarSelect(selectProducto, 'Seleccioná un producto');
  llenarSelect(selectProducto, productos);

  limpiarSelect(selectProveedor, 'Seleccioná un proveedor');
  llenarSelect(selectProveedor, proveedores);
}

export async function initFormulario({ onRegistrada } = {}) {
  const form = $('#form-registrar-entrada');
  if (!form) return;

  const inputCantidad = $('#entrada-cantidad');
  const mensaje = $('#entrada-mensaje');
  const boton = form.querySelector('button[type="submit"]');

  try {
    await cargarCombos();
  } catch (error) {
    mostrarMensaje(mensaje, `No se pudieron cargar los datos: ${error.message}`, 'error');
    return;
  }

  form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    ocultarMensaje(mensaje);

    const producto_id = $('#entrada-producto').value;
    const proveedor_id = $('#entrada-proveedor').value;
    const cantidad = Number(inputCantidad.value);

    if (!producto_id) return mostrarMensaje(mensaje, 'Elegí un producto.', 'error');
    if (!cantidad || cantidad < 1) return mostrarMensaje(mensaje, 'La cantidad debe ser mayor a cero.', 'error');
    if (!proveedor_id) return mostrarMensaje(mensaje, 'Elegí un proveedor.', 'error');

    boton.disabled = true;

    try {
      const respuesta = await registrarEntrada({ producto_id, cantidad, proveedor_id });
      mostrarMensaje(mensaje, `Entrada registrada. Nuevo stock: ${respuesta.nuevo_stock}.`, 'exito');
      form.reset();
      onRegistrada?.(respuesta);
    } catch (error) {
      mostrarMensaje(mensaje, error.message, 'error');
    } finally {
      boton.disabled = false;
    }
  });
}
