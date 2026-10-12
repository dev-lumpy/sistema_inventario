// static/js/admin/inicio/js/core/http.js
// static/js/admin/inicio/js/core/http.js
import { CONFIG } from './config.js';

export async function getJSON(endpoint) {
  const res = await fetch(CONFIG.API_BASE + endpoint, {
    headers: { Accept: 'application/json' },
    credentials: 'include',
  });

  if (!res.ok) {
    let detalle = null;
    try { detalle = await res.json(); } catch {}

    if (res.status >= 500) {
      throw new Error(detalle?.detail || 'Error del servidor');
    }
    if (res.status === 404) {
      throw new Error(detalle?.detail || 'Recurso no encontrado');
    }
    if (res.status === 401 || res.status === 403) {
      throw new Error(detalle?.detail || 'No autorizado');
    }
  console.log(endpoint)
  console.log(endpoint)
  console.log(endpoint)
    throw new Error(detalle?.detail || `Error ${res.status}`);
  }

  return res.json();
}
