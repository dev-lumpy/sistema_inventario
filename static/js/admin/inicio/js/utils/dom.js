// static/js/admin/inicio/js/utils/dom.js
export const $ = (selector, ctx = document) => ctx.querySelector(selector);

/** Crea un elemento sin usar innerHTML (evita XSS con datos del servidor). */
export function crearEl(tag, { clase, texto, attrs = {} } = {}) {
  const el = document.createElement(tag);
  if (clase) el.className = clase;
  if (texto !== undefined) el.textContent = texto;
  Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
  return el;
}
