 /* tabla.js — Tabla de productos existentes + buscador */

import { $, escaparHtml, formatearPrecio } from './utils.js';
import { state } from './state.js';

const tbody = $('tbody-productos');
const buscador = $('buscador-productos');

// ---- Helpers de render ----

function nombreCategoria(categoriaId) {
  const cat = state.categorias.find((c) => c.id === categoriaId);
  return cat ? cat.nombre : '—';
}
function filaEstado(mensaje, icono, esError = false) {
  return `
    <tr class="tabla-estado${esError ? ' error' : ''}">
      <td colspan="6"><i class="fa-solid ${icono}"></i> ${mensaje}</td>
    </tr>
  `;
}

function badgeStock(p) {
  const actual = Number(p.stock_actual ?? p.cantidad_inicial);
  const stockBajo = actual <= Number(p.stock_minimo);

  return stockBajo
    ? '<span class="badge badge-bajo"><i class="fa-solid fa-triangle-exclamation"></i> Stock bajo</span>'
    : '<span class="badge badge-ok"><i class="fa-solid fa-circle-check"></i> Normal</span>';
}

function filaProducto(p) {
  return `
    <tr data-id="${p.id}">
      <td>${escaparHtml(p.nombre)}</td>
      <td>${escaparHtml(nombreCategoria(p.categoria))}</td>
      <td>${formatearPrecio(p.precio_unitario)}</td>
      <td>${escaparHtml(p.stock_actual)}</td>
      <td>${badgeStock(p)}</td>
      <td class="acciones">
        <button type="button" class="btn-icon editar" data-action="editar" data-id="${p.id}" title="Editar">
          <i class="fa-solid fa-pen"></i>
        </button>
        <button type="button" class="btn-icon eliminar" data-action="eliminar" data-id="${p.id}" title="Eliminar">
          <i class="fa-solid fa-trash"></i>
        </button>
      </td>
    </tr>
  `;
}

// ---- Render público ----

export function mostrarCargando() {
  tbody.innerHTML = filaEstado('Cargando productos...', 'fa-spinner fa-spin');
}

export function mostrarError() {
  tbody.innerHTML = filaEstado('No se pudieron cargar los productos.', 'fa-triangle-exclamation', true);
}

export function renderTabla() {
  const filtro = state.filtroTexto.toLowerCase();
  const lista = state.productos.filter((p) => p.nombre.toLowerCase().includes(filtro));

  if (lista.length === 0) {
    const mensaje = state.productos.length === 0
      ? 'Todavía no hay productos registrados.'
      : 'No se encontraron productos con ese nombre.';
    tbody.innerHTML = filaEstado(mensaje, 'fa-box-open');
    return;
  }

  tbody.innerHTML = lista.map(filaProducto).join('');
}

// ---- Init ----

export function initTabla({ onEditar, onEliminar }) {
  tbody.addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-action]');
    if (!btn) return;

    const { action, id } = btn.dataset;
    if (action === 'editar') onEditar(id);
    if (action === 'eliminar') onEliminar(id);
  });

  buscador.addEventListener('input', () => {
    state.filtroTexto = buscador.value.trim();
    renderTabla();
  });
}
