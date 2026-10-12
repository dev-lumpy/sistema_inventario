 /* formulario.js — Zona donde se crea / edita un producto */

import { $ } from './utils.js';
import { state } from './state.js';
import { guardarProducto } from './api.js';
import { cambiarEstadoBoton, bloquearBoton, iniciarBoton } from './boton-guardar.js';

const form = $('form-producto');
const inputNombre = $('producto-nombre');
const selectCategoria = $('producto-categoria');
const inputPrecio = $('producto-precio');
const inputCantidad = $('producto-cantidad');
const inputStockMinimo = $('producto-stock-minimo');
const tituloForm = $('titulo-form-producto');
const btnCancelar = $('btn-cancelar-producto');

let productoEditandoId = null; // null = creando, valor = editando ese producto

// ---- Render ----

export function renderCategorias() {
  selectCategoria.innerHTML = '<option value="">Seleccioná una categoría</option>';
  state.categorias.forEach((cat) => {
    const opt = document.createElement('option');
    opt.value = cat.id;
    opt.textContent = cat.nombre;
    selectCategoria.appendChild(opt);
  });
}

// ---- Acciones ----

export function resetFormulario() {
  form.reset();
  productoEditandoId = null;
  tituloForm.textContent = 'Nuevo producto';
}

export function cargarEnFormulario(producto) {
  productoEditandoId = producto.id;
  inputNombre.value = producto.nombre;
  selectCategoria.value = producto.categoria;
  inputPrecio.value = producto.precio_unitario;
  inputCantidad.value = producto.cantidad_inicial;
  inputStockMinimo.value = producto.stock_minimo;

  tituloForm.textContent = 'Editar producto';
  form.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function leerFormulario() {
  const payload = {
    nombre: inputNombre.value.trim(),
    categoria: selectCategoria.value,
    precio_unitario: inputPrecio.value,
    stock_minimo: inputStockMinimo.value,
    cantidad_inicial: inputCantidad.value,
  };
  if (productoEditandoId !== null) payload.id = productoEditandoId;
  return payload;
}

async function onSubmit(e, onGuardado) {
  e.preventDefault();

  const esEdicion = productoEditandoId !== null;
  const payload = leerFormulario();

  cambiarEstadoBoton('CARGANDO');
  bloquearBoton(true);

  try {
    const guardado = await guardarProducto(payload, esEdicion);
    cambiarEstadoBoton('CARGADO');
    resetFormulario();
    onGuardado(guardado, esEdicion); // avisa al archivo principal
  } catch (err) {
    console.error('Error guardando producto:', err);
    alert(err.message || 'No se pudo guardar el producto. Intentá de nuevo.');
  } finally {
    bloquearBoton(false);
    cambiarEstadoBoton('DEFAULT');
  }
}

// ---- Init ----

export function initFormulario({ onGuardado }) {
  iniciarBoton();
  form.addEventListener('submit', (e) => onSubmit(e, onGuardado));
  btnCancelar.addEventListener('click', resetFormulario);
}
