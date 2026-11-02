import { CONFIG } from './config.js';

function construirUrl(path) {
  if (/^https?:\/\//.test(path) || path.startsWith('/')) return path;
  return `${CONFIG.API_BASE}/${path.replace(/^\//, '')}`;
}

function mensajeDeError(data, status) {
  if (data) {
    if (typeof data === 'string' && data.trim()) return data;
    if (typeof data.detail === 'string') return data.detail;

    if (data.error) {
      const faltantes = Array.isArray(data.campos_faltantes) && data.campos_faltantes.length
        ? ` Faltan: ${data.campos_faltantes.join(', ')}.`
        : '';
      return `${data.error}.${faltantes}`.replace(/\.\./g, '.');
    }

    if (data.error_campo) {
      const valor = data.error_campo.mensaje
        || data.error_campo.detail
        || data.error_campo;
      if (typeof valor === 'string') return valor;
    }

    const campos = Object.entries(data)
      .filter(([, valor]) => valor != null && valor !== '')
      .map(([campo, valor]) => `${campo}: ${Array.isArray(valor) ? valor.join(' ') : valor}`);

    if (campos.length) return campos.join('. ');
  }

  if (status >= 500) return 'Error del servidor. Intentá de nuevo más tarde.';
  if (status === 401) return 'Tu sesión expiró. Volvé a iniciar sesión.';
  if (status === 403) return 'No tenés permiso para esta acción.';
  if (status === 404) return 'No se encontró el recurso solicitado.';
  if (status === 400) return 'Solicitud inválida. Revisá los datos.';
  return `Respuesta inesperada del servidor (${status}).`;
}

async function leerCuerpo(res) {
  if (res.status === 204) return null;

  const tipo = res.headers.get('content-type') || '';
  if (!tipo.includes('application/json')) return null;

  try {
    return await res.json();
  } catch {
    return null;
  }
}

export async function request(path, { method = 'GET', body, headers = {} } = {}) {
  const opciones = {
    method,
    credentials: 'include',
    headers: { Accept: 'application/json', ...headers },
  };

  if (body !== undefined) {
    opciones.headers['Content-Type'] = 'application/json';
    opciones.body = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(construirUrl(path), opciones);
  } catch {
    throw new Error('No hay conexión con el servidor.');
  }

  const data = await leerCuerpo(res);

  if (!res.ok) {
    const error = new Error(mensajeDeError(data, res.status));
    error.status = res.status;
    error.data = data;
    throw error;
  }

  return data;
}

export const getJSON = (path) => request(path);
export const postJSON = (path, body) => request(path, { method: 'POST', body });
export const putJSON = (path, body) => request(path, { method: 'PUT', body });
export const deleteJSON = (path) => request(path, { method: 'DELETE' });
