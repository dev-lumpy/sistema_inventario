import { obtenerAlertasStock, obtenerResumenHoy } from './api.js';
import { renderAlertas, renderAlertasError } from './alertas.js';
import { renderResumen, resetResumen } from './resumen.js';

export async function cargarInicio() {
  resetResumen();

  try {
    const [alertas, resumen] = await Promise.all([
      obtenerAlertasStock(),
      obtenerResumenHoy(),
    ]);

    renderAlertas(alertas);
    renderResumen({ ...resumen, alertas: alertas.length });
  } catch (error) {
    console.error('[inicio]', error);
    renderAlertasError('No se pudo cargar la información. Intentá de nuevo.');
  }
}

export function initInicio() {
  if (!document.getElementById('inicio')) return;

  cargarInicio();

  document.addEventListener('seccion:activada', (evento) => {
    if (evento.detail.seccion === 'inicio') cargarInicio();
  });
}
