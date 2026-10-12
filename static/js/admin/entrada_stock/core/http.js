// static/js/admin/entrada_stock/js/core/http.js
import { CONFIG } from './config.js';

async function manejarRespuesta(res) {
  if (res.ok) return res.json();

  let detalle = null;
  try { detalle = await res.json(); } catch {}

  const mensaje =
    detalle?.detail ||
    detalle?.mensaje ||
    Object.values(detalle || {}).flat().join(' ') ||
    `Error ${res.status}`;

  if (res.status >= 500) throw new Error('Error del servidor. Intentá más tarde.');
  if (res.status === 404) throw new Error('Recurso no encontrado.');
  if (res.status === 401 || res.status === 403) throw new Error('No autorizado.');
  throw new Error(mensaje);
}

export async function getJSON(endpoint) {
  const res = await fetch(CONFIG.API_BASE + endpoint, {
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });
  return manejarRespuesta(res);
}

export async function postJSON(endpoint, data) {
  const res = await fetch(CONFIG.API_BASE + endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(data),
  });
  return manejarRespuesta(res);
}
