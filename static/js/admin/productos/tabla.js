import { crearFilaEstado, escaparHtml } from '../../shared/core/dom.js';
import { formatearPrecio } from '../../shared/core/format.js';
import { state } from './state.js';

const getTbody = () => document.getElementById('tbody-productos');
const getBuscador = () => document.getElementById('buscador-productos');

function nombreCategoria(categoriaId) {
  const categoria = (state.categorias || []).find(
    (item) => String(item.id) === String(categoriaId),
  );
  return categoria ? categoria.nombre : '—';
}

function badgeStock(producto) {
  const actual = Number(producto.stock_actual ?? 0);
  const minimo = Number(producto.stock_minimo) || 0;

  return actual <= minimo
    ? '<span class="badge badge-bajo"><i class="fa-solid fa-triangle-exclamation"></i> Stock bajo</span>'
    : '<span class="badge badge-ok"><i class="fa-solid fa-circle-check"></i> Normal</span>';
}

function filaProducto(producto) {
  return `
    <tr data-id="${producto.id}">
      <td>${escaparHtml(producto.nombre ?? '')}</td>
      <td>${escaparHtml(nombreCategoria(producto.categoria))}</td>
      <td>${formatearPrecio(producto.precio_unitario)}</td>
      <td>${escaparHtml(String(producto.stock_actual ?? ''))}</td>
      <td>${badgeStock(producto)}</td>
      <td class="acciones">
        <button type="button" class="btn-icon editar" data-action="editar" data-id="${producto.id}" title="Editar">
          <i class="fa-solid fa-pen"></i>
        </button>
      </td>
    </tr>
  `;
}

export function mostrarCargando() {
  const tbody = getTbody();
  if (!tbody) return;
  tbody.replaceChildren(crearFilaEstado(6, 'Cargando productos...', { icono: 'fa-spinner fa-spin' }));
}

export function mostrarError() {
  const tbody = getTbody();
  if (!tbody) return;
  tbody.replaceChildren(crearFilaEstado(6, 'No se pudieron cargar los productos.', {
    icono: 'fa-triangle-exclamation',
    error: true,
  }));
}

export function renderTabla() {
  const tbody = getTbody();
  if (!tbody) {
    console.warn('[productos] renderTabla: no se encontró #tbody-productos');
    return;
  }

  const filtro = (state.filtroTexto || '').toLowerCase();
  const productos = Array.isArray(state.productos) ? state.productos : [];
  const lista = productos.filter(
    (producto) => String(producto?.nombre ?? '').toLowerCase().includes(filtro),
  );

  if (lista.length === 0) {
    const mensaje = productos.length === 0
      ? 'Todavía no hay productos registrados.'
      : 'No se encontraron productos con ese nombre.';

    tbody.replaceChildren(crearFilaEstado(6, mensaje, { icono: 'fa-box-open' }));
    return;
  }

  tbody.innerHTML = lista.map(filaProducto).join('');
}

export function initTabla({ onEditar }) {
  const tbody = getTbody();
  if (!tbody) return;

  if (tbody.dataset.eventos === '1') return;
  tbody.dataset.eventos = '1';

  tbody.addEventListener('click', (evento) => {
    const boton = evento.target.closest('button[data-action="editar"]');
    if (!boton) return;
    onEditar(boton.dataset.id);
  });

  const buscador = getBuscador();
  buscador?.addEventListener('input', () => {
    state.filtroTexto = buscador.value.trim();
    renderTabla();
  });
}
