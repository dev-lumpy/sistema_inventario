import { $, crearEl, crearFilaEstado } from '../../shared/core/dom.js';
import { formatearPrecio } from '../../shared/core/format.js';
import { obtenerCategorias, obtenerProductos } from '../api.js';

const COLUMNAS = 5;

const state = {
  productos: [],
  categorias: [],
  filtroActivo: null,
};

function aLista(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

function normalizar(valor) {
  return String(valor ?? '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim()
    .toLowerCase();
}

function nombreCategoria(id) {
  const categoria = state.categorias.find(
    (item) => String(item.id) === String(id),
  );
  return categoria ? categoria.nombre : '—';
}

function estadoProducto(producto) {
  const stock = Number(producto.stock_actual ?? 0);
  const minimo = Number(producto.stock_minimo ?? 0);

  if (stock <= 0) {
    return { clave: 'agotado', texto: 'Agotado', clase: 'badge-bajo' };
  }

  if (stock <= minimo) {
    return { clave: 'bajo', texto: 'Bajo', clase: 'badge-bajo' };
  }

  return { clave: 'disponible', texto: 'Disponible', clase: 'badge-ok' };
}

function productoFiltrado(producto) {
  if (state.filtroActivo === 'texto') {
    const texto = normalizar($('#filtro-texto')?.value);
    if (!texto) return true;
    return normalizar(producto.nombre).includes(texto);
  }

  if (state.filtroActivo === 'categoria') {
    const categoria = $('#filtro-categoria')?.value;
    if (!categoria) return true;
    return String(producto.categoria) === String(categoria);
  }

  if (state.filtroActivo === 'estado') {
    const estado = $('#filtro-estado')?.value;
    if (!estado) return true;
    return estadoProducto(producto).clave === estado;
  }

  return true;
}

function renderVacio(visible, mensaje) {
  const vacio = $('#inventario-vacio');
  if (!vacio) return;

  if (mensaje) vacio.textContent = mensaje;
  vacio.hidden = !visible;
}

function renderTabla() {
  const tbody = $('#tbody-inventario');
  if (!tbody) return;

  const filtrados = state.productos.filter(productoFiltrado);

  tbody.replaceChildren();

  if (!filtrados.length) {
    renderVacio(
      true,
      state.filtroActivo
        ? 'No hay productos que coincidan con los filtros.'
        : 'No hay productos registrados.',
    );
    return;
  }

  renderVacio(false);

  for (const producto of filtrados) {
    const estado = estadoProducto(producto);

    const tdEstado = crearEl('td');
    tdEstado.appendChild(crearEl('span', {
      clase: `badge ${estado.clase}`,
      texto: estado.texto,
    }));

    const tr = document.createElement('tr');
    tr.append(
      crearEl('td', { texto: producto.nombre ?? '—' }),
      crearEl('td', { texto: nombreCategoria(producto.categoria) }),
      crearEl('td', { texto: formatearPrecio(producto.precio_unitario) }),
      crearEl('td', { texto: String(producto.stock_actual ?? 0) }),
      tdEstado,
    );

    tbody.appendChild(tr);
  }
}

function renderCargando() {
  const tbody = $('#tbody-inventario');
  if (tbody) {
    tbody.replaceChildren(crearFilaEstado(COLUMNAS, 'Cargando productos...', {
      icono: 'fa-spinner fa-spin',
    }));
  }
  renderVacio(false);
}

function renderError(mensaje) {
  const tbody = $('#tbody-inventario');
  if (tbody) {
    tbody.replaceChildren(crearFilaEstado(COLUMNAS, mensaje, {
      icono: 'fa-triangle-exclamation',
      error: true,
    }));
  }
  renderVacio(false);
}

function llenarCategorias() {
  const select = $('#filtro-categoria');
  if (!select) return;

  const seleccionada = select.value;

  select.replaceChildren(
    crearEl('option', { texto: 'Todas', attrs: { value: '' } }),
  );

  for (const categoria of state.categorias) {
    select.appendChild(crearEl('option', {
      texto: categoria.nombre,
      attrs: { value: categoria.id },
    }));
  }

  select.value = state.categorias.some(
    (categoria) => String(categoria.id) === String(seleccionada),
  ) ? seleccionada : '';
}

async function cargar() {
  renderCargando();

  try {
    const [productos, categorias] = await Promise.all([
      obtenerProductos(),
      obtenerCategorias().catch(() => []),
    ]);

    state.productos = aLista(productos).sort(
      (a, b) => String(a.nombre ?? '').localeCompare(String(b.nombre ?? ''), 'es'),
    );
    state.categorias = aLista(categorias);

    llenarCategorias();
    renderTabla();
  } catch (error) {
    renderError(`No se pudieron cargar los productos: ${error.message}`);
  }
}

function activarTexto(inputTexto, selectCategoria, selectEstado) {
  if (!inputTexto.value.trim()) {
    state.filtroActivo = null;
  } else {
    state.filtroActivo = 'texto';
    selectCategoria.value = '';
    selectEstado.value = '';
  }

  renderTabla();
}

function activarCategoria(inputTexto, selectCategoria, selectEstado) {
  if (!selectCategoria.value) {
    state.filtroActivo = null;
  } else {
    state.filtroActivo = 'categoria';
    inputTexto.value = '';
    selectEstado.value = '';
  }

  renderTabla();
}

function activarEstado(inputTexto, selectCategoria, selectEstado) {
  if (!selectEstado.value) {
    state.filtroActivo = null;
  } else {
    state.filtroActivo = 'estado';
    inputTexto.value = '';
    selectCategoria.value = '';
  }

  renderTabla();
}

export async function initInventario() {
  const form = $('#form-filtros-inventario');
  if (!form) return;

  const inputTexto = $('#filtro-texto');
  const selectCategoria = $('#filtro-categoria');
  const selectEstado = $('#filtro-estado');
  const btnLimpiar = $('#btn-limpiar-filtros');

  let temporizador;

  inputTexto?.addEventListener('input', () => {
    clearTimeout(temporizador);
    temporizador = setTimeout(() => {
      activarTexto(inputTexto, selectCategoria, selectEstado);
    }, 250);
  });

  selectCategoria?.addEventListener('change', () => {
    activarCategoria(inputTexto, selectCategoria, selectEstado);
  });

  selectEstado?.addEventListener('change', () => {
    activarEstado(inputTexto, selectCategoria, selectEstado);
  });

  form.addEventListener('submit', (evento) => {
    evento.preventDefault();

    if (selectEstado?.value) {
      activarEstado(inputTexto, selectCategoria, selectEstado);
      return;
    }

    if (selectCategoria?.value) {
      activarCategoria(inputTexto, selectCategoria, selectEstado);
      return;
    }

    activarTexto(inputTexto, selectCategoria, selectEstado);
  });

  btnLimpiar?.addEventListener('click', () => {
    if (inputTexto) inputTexto.value = '';
    if (selectCategoria) selectCategoria.value = '';
    if (selectEstado) selectEstado.value = '';

    state.filtroActivo = null;
    renderTabla();
    inputTexto?.focus();
  });

  await cargar();

  document.addEventListener('seccion:activada', (evento) => {
    if (evento.detail?.seccion === 'inventario') cargar();
  });
}
