import { $ } from '../../shared/core/dom.js';
import { formatearNumero } from '../../shared/core/format.js';

const IDS = {
  ventas: '#stat-ventas-hoy',
  entradas: '#stat-entradas-hoy',
  alertas: '#stat-productos-bajo',
};

function setStat(selector, valor) {
  const el = $(selector);
  if (el) el.textContent = valor === null ? '—' : formatearNumero(valor);
}

export function renderResumen({ ventas, entradas, alertas }) {
  setStat(IDS.ventas, ventas);
  setStat(IDS.entradas, entradas);
  setStat(IDS.alertas, alertas);
}

export function resetResumen() {
  renderResumen({ ventas: null, entradas: null, alertas: null });
}
