// static/js/admin/inicio/js/inicio/alertas.js
import { $, crearEl } from '../utils/dom.js';

/** Nivel de gravedad según el stock respecto al mínimo. */
export function nivelAlerta({ stock, stock_minimo }) {
  if (stock <= 0) return { clave: 'agotado', texto: 'Agotado' };
  if (stock <= stock_minimo / 2) return { clave: 'critico', texto: 'Crítico' };
  return { clave: 'bajo', texto: 'Bajo' };
}

function crearItem(producto) {
  const nivel = nivelAlerta(producto);
  const li = crearEl('li', { clase: `alerta-item alerta-${nivel.clave}` });

  li.append(
    crearEl('span', { clase: 'alerta-nombre', texto: producto.nombre }),
    crearEl('span', {
      clase: 'alerta-stock',
      texto: `Stock: ${producto.stock} / mín. ${producto.stock_minimo}`,
    }),
    crearEl('span', { clase: 'alerta-badge', texto: nivel.texto }),
  );
  return li;
}

export function renderAlertas(productos) {
  const lista = $('#lista-alertas');
  const vacio = $('#alertas-vacio');
  if (!lista || !vacio) return;

  // Más graves primero (menor proporción stock/mínimo)
  const ordenados = [...productos].sort(
    (a, b) => a.stock / (a.stock_minimo || 1) - b.stock / (b.stock_minimo || 1),
  );

  lista.replaceChildren(...ordenados.map(crearItem));
  vacio.textContent = 'No hay productos en alerta. Todo en orden.';
  vacio.hidden = ordenados.length > 0;
}

export function renderAlertasError(mensaje) {
  const lista = $('#lista-alertas');
  const vacio = $('#alertas-vacio');
  if (!lista || !vacio) return;
  lista.replaceChildren();
  vacio.textContent = mensaje;
  vacio.hidden = false;
}
