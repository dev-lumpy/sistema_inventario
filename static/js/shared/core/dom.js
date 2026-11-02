export const $ = (selector, contexto = document) => contexto.querySelector(selector);
export const $$ = (selector, contexto = document) => [...contexto.querySelectorAll(selector)];

export function crearEl(tag, { clase, texto, attrs = {} } = {}) {
  const el = document.createElement(tag);
  if (clase) el.className = clase;
  if (texto !== undefined) el.textContent = texto;
  for (const [clave, valor] of Object.entries(attrs)) {
    el.setAttribute(clave, valor);
  }
  return el;
}

export function escaparHtml(valor) {
  return String(valor ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function limpiarSelect(select, placeholder) {
  select.replaceChildren();
  if (!placeholder) return;

  const opcion = document.createElement('option');
  opcion.value = '';
  opcion.textContent = placeholder;
  select.appendChild(opcion);
}

export function llenarSelect(select, items, {
  valorDe = (item) => item.id,
  textoDe = (item) => item.nombre,
} = {}) {
  for (const item of items) {
    const opcion = document.createElement('option');
    opcion.value = valorDe(item);
    opcion.textContent = textoDe(item);
    select.appendChild(opcion);
  }
}

export function crearFilaEstado(colspan, mensaje, { icono = 'fa-circle-info', error = false } = {}) {
  const tr = document.createElement('tr');
  tr.className = `tabla-estado${error ? ' error' : ''}`;

  const td = document.createElement('td');
  td.colSpan = colspan;

  const iconoEl = document.createElement('i');
  iconoEl.className = `fa-solid ${icono}`;

  td.append(iconoEl, document.createTextNode(` ${mensaje}`));
  tr.appendChild(td);
  return tr;
}

export function mostrarMensaje(el, texto, tipo = 'info') {
  if (!el) return;
  el.textContent = texto;
  el.className = `mensaje mensaje-${tipo}`;
  el.hidden = !texto;
}

export function ocultarMensaje(el) {
  if (!el) return;
  el.textContent = '';
  el.hidden = true;
}
