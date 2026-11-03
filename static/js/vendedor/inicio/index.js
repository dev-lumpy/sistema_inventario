import { $, crearEl } from '../../shared/core/dom.js';
import { obtenerAlertasStock } from '../api.js';

function nivelAlerta({ stock, stock_minimo: minimo }) {
  if (stock <= 0) return { clave: 'agotado', texto: 'Agotado' };
  if (stock <= minimo / 2) return { clave: 'critico', texto: 'Crítico' };
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

function renderAlertas(productos) {
  const lista = $('.lista-alertas');
  const vacio = $('#alertas-vacio');
  if (!lista || !vacio) return;

  const ordenados = [...productos].sort(
    (a, b) => a.stock / (a.stock_minimo || 1) - b.stock / (b.stock_minimo || 1),
  );

  lista.replaceChildren(...ordenados.map(crearItem));
  vacio.textContent = 'No hay productos en alerta. Todo en orden.';
  vacio.hidden = ordenados.length > 0;
}

function renderError(mensaje) {
  const lista = $('#lista-alertas');
  const vacio = $('#alertas-vacio');

  if (lista) lista.replaceChildren();

  if (vacio) {
    vacio.textContent = mensaje;
    vacio.hidden = false;
  }
}

async function cargar() {
  try {
    const productos = await obtenerAlertasStock();
    renderAlertas(Array.isArray(productos) ? productos : []);
  } catch (error) {
    renderError(`No se pudieron cargar las alertas: ${error.message}`);
  }
}

export async function initInicio() {
  const lista = $('.lista-alertas');
  
  if (!lista) return;

  await cargar();

  document.addEventListener('seccion:activada', (evento) => {
    if (evento.detail?.seccion === 'inicio') cargar();
  });
}
