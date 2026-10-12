// static/js/admin/entrada_stock/js/utils/dom.js
export const $ = (sel, raiz = document) => raiz.querySelector(sel);
export const $$ = (sel, raiz = document) => [...raiz.querySelectorAll(sel)];

export function crearEl(tag, { clase, texto, attrs } = {}) {
  const el = document.createElement(tag);
  if (clase) el.className = clase;
  if (texto != null) el.textContent = texto;
  if (attrs) for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  return el;
}

export function limpiarSelect(select, placeholder) {
  select.replaceChildren();
  if (placeholder) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = placeholder;
    select.appendChild(opt);
  }
}

export function llenarSelect(select, items, { valorDe = (x) => x.id, textoDe = (x) => x.nombre } = {}) {
  for (const item of items) {
    const opt = document.createElement('option');
    opt.value = valorDe(item);
    opt.textContent = textoDe(item);
    select.appendChild(opt);
  }
}

export function mostrarMensaje(el, texto, tipo = 'info') {
  el.textContent = texto;
  el.className = `mensaje mensaje-${tipo}`;
  el.hidden = !texto;
}

export function ocultarMensaje(el) {
  el.textContent = '';
  el.hidden = true;
}
