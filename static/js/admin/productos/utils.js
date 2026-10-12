 /* utils.js — Funciones pequeñas y reutilizables (sin lógica de negocio) */

export const $ = (id) => document.getElementById(id);

export function escaparHtml(valor) {
  return String(valor ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function formatearPrecio(valor) {
  const num = Number(valor) || 0;
  return num.toLocaleString('es-BO', { style: 'currency', currency: 'BOB' });
}
