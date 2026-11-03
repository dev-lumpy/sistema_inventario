import { $ } from '../../shared/core/dom.js';
import { state } from './state.js';
import { guardarProducto } from './api.js';
import { cambiarEstadoBoton, bloquearBoton, iniciarBoton } from './boton-guardar.js';
import { cargarProductos } from '../../shared/ventas/formulario.js';

const form = $('#form-producto');
const inputNombre = $('#producto-nombre');
const selectCategoria = $('#producto-categoria');
const inputPrecio = $('#producto-precio');
const inputCantidad = $('#producto-cantidad');
const inputStockMinimo = $('#producto-stock-minimo');
const tituloForm = $('#titulo-form-producto');
const btnCancelar = $('#btn-cancelar-producto');

let productoEditandoId = null;

export function renderCategorias() {
  if (!selectCategoria) return;

  selectCategoria.replaceChildren();

  const placeholder = document.createElement('option');
  placeholder.value = '';
  placeholder.textContent = 'Seleccioná una categoría';
  selectCategoria.appendChild(placeholder);

  for (const categoria of state.categorias) {
    const opcion = document.createElement('option');
    opcion.value = categoria.id;
    opcion.textContent = categoria.nombre;
    selectCategoria.appendChild(opcion);
  }
}

export function resetFormulario() {
  form?.reset();
  productoEditandoId = null;
  if (tituloForm) tituloForm.textContent = 'Nuevo producto';
  if (inputCantidad) inputCantidad.disabled = false;
}

export function cargarEnFormulario(producto) {
  productoEditandoId = producto.id;

  inputNombre.value = producto.nombre;
  selectCategoria.value = producto.categoria;
  inputPrecio.value = producto.precio_unitario;
  inputCantidad.value = producto.stock_actual ?? 0;
  inputStockMinimo.value = producto.stock_minimo;

  inputCantidad.disabled = true;
  tituloForm.textContent = 'Editar producto';
  form.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function leerFormulario() {
  const esEdicion = productoEditandoId !== null;
  const cantidad = Number(inputCantidad.value) || 0;

  const payload = {
    nombre: inputNombre.value.trim(),
    categoria: selectCategoria.value,
    precio_unitario: inputPrecio.value,
    stock_minimo: inputStockMinimo.value,
    // En edición el backend ignora este campo, pero lo exige con mínimo 1.
    cantidad_inicial: esEdicion ? Math.max(1, cantidad) : cantidad,
  };

  if (esEdicion) payload.id = productoEditandoId;
  return payload;
}

async function onSubmit(evento, onGuardado) {
  evento.preventDefault();

  const esEdicion = productoEditandoId !== null;
  const payload = leerFormulario();


  cambiarEstadoBoton('CARGANDO');
  bloquearBoton(true);

  try {
    const guardado = await guardarProducto(payload, esEdicion);
    cambiarEstadoBoton('CARGADO');
    await cargarProductos().catch((error) => {
      console.error('[producto-form] No se pudo actualizar el select de ventas:', error);
    });
    resetFormulario();
    await onGuardado(guardado, esEdicion);
    setTimeout(() => cambiarEstadoBoton('DEFAULT'), 1200);
  } catch (error) {
    console.error('[producto-form] Error guardando producto:', error);
    cambiarEstadoBoton('DEFAULT');
    alert(error.message || 'No se pudo guardar el producto. Intentá de nuevo.');
  } finally {
    bloquearBoton(false);
  }
}

export function initFormulario({ onGuardado }) {
  if (!form) {
    console.warn('[producto-form] initFormulario: formulario no encontrado');
    return;
  }

  iniciarBoton();
  form.addEventListener('submit', (evento) => onSubmit(evento, onGuardado));
  btnCancelar?.addEventListener('click', resetFormulario);
}
