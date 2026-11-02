import { state } from './state.js';
import { fetchProductos, fetchCategorias } from './api.js';
import { initFormulario, renderCategorias, cargarEnFormulario } from './formulario.js';
import { initTabla, renderTabla, mostrarCargando, mostrarError } from './tabla.js';
import { cambiarEstadoBoton } from './boton-guardar.js';

let inicializado = false;
let escuchandoSeccion = false;

const buscarPorId = (id) => (state.productos || []).find(
  (producto) => String(producto.id) === String(id),
);

function aLista(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

async function cargarCategorias() {
  try {
    state.categorias = aLista(await fetchCategorias());
    renderCategorias();
  } catch (error) {
    console.error('[productos] Error cargando categorías:', error);
  }
}

async function cargarProductos() {
  try {
    state.productos = aLista(await fetchProductos());
    return true;
  } catch (error) {
    console.error('[productos] Error cargando productos:', error);
    return false;
  }
}

async function refrescar() {
  mostrarCargando();

  const [, productosOk] = await Promise.all([cargarCategorias(), cargarProductos()]);

  if (!productosOk) {
    mostrarError();
    return false;
  }

  try {
    renderTabla();
    return true;
  } catch (error) {
    console.error('[productos] Error renderizando tabla:', error);
    mostrarError();
    return false;
  }
}

async function onGuardado() {
  await refrescar();
}

function onEditar(id) {
  const producto = buscarPorId(id);
  if (producto) cargarEnFormulario(producto);
  else console.warn('[productos] onEditar: producto no encontrado', { id });
}

export async function initProductos() {
  cambiarEstadoBoton('DEFAULT');

  if (!document.getElementById('form-producto')) {
    return;
  }

  if (!inicializado) {
    initFormulario({ onGuardado });
    initTabla({ onEditar });
    inicializado = true;
  }

  await refrescar();

  if (escuchandoSeccion) return;
  escuchandoSeccion = true;

  document.addEventListener('seccion:activada', async (evento) => {
    if (evento.detail?.seccion !== 'productos') return;
    await refrescar();
  });
}
