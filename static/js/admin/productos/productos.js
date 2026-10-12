/* productos.js — Punto de entrada. Solo conecta los módulos entre sí.

   Cargar en el HTML con:
   <script type="module" src="/js/productos/productos.js"></script>
*/

import { state } from './state.js';
import { fetchProductos, fetchCategorias, eliminarProducto } from './api.js';
import { initFormulario, renderCategorias, cargarEnFormulario } from './formulario.js';
import { initTabla, renderTabla, mostrarCargando, mostrarError } from './tabla.js';

const buscarPorId = (id) => state.productos.find((p) => String(p.id) === String(id));

// ---- Carga de datos ----

async function cargarCategorias() {
  try {
    state.categorias = await fetchCategorias();
    renderCategorias();
  } catch (err) {
    console.error('Error cargando categorías:', err);
  }
}

async function cargarProductos() {
  try {
    state.productos = await fetchProductos();
    return true;
  } catch (err) {
    console.error('Error cargando productos:', err);
    mostrarError();
    return false;
  }
}

// ---- Qué pasa cuando la tabla o el formulario avisan algo ----

function onGuardado(guardado, esEdicion) {
  if (esEdicion) {
    state.productos = state.productos.map((p) => (String(p.id) === String(guardado.id) ? guardado : p));
  } else {
    state.productos.push(guardado);
  }
  renderTabla();
}

function onEditar(id) {
  const producto = buscarPorId(id);
  if (producto) cargarEnFormulario(producto);
}

async function onEliminar(id) {
  const producto = buscarPorId(id);
  const nombre = producto ? producto.nombre : 'este producto';
  if (!confirm(`¿Eliminar "${nombre}"? Esta acción no se puede deshacer.`)) return;

  try {
    await eliminarProducto(id);
    state.productos = state.productos.filter((p) => String(p.id) !== String(id));
    renderTabla();
  } catch (err) {
    console.error('Error eliminando producto:', err);
    alert('No se pudo eliminar el producto.');
  }
}

// ---- Init ----

async function init() {
  if (!document.getElementById('form-producto')) return; // la sección no está en esta página

  initFormulario({ onGuardado });
  initTabla({ onEditar, onEliminar });

  mostrarCargando();
  const [, productosOk] = await Promise.all([cargarCategorias(), cargarProductos()]);
  if (productosOk) renderTabla(); // se dibuja cuando ya hay categorías Y productos
}

init();
