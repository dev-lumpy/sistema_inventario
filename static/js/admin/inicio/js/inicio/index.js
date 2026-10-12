// static/js/admin/inicio/js/inicio/index.js
import { obtenerAlertasStock, obtenerResumenHoy } from '../services/inicio.service.js';
import { renderAlertas, renderAlertasError } from './alertas.js';
import { renderResumen, resetResumen } from './resumen.js';
import { initAccesos } from './accesos.js';

export async function cargarInicio() {
  resetResumen();
  try {
    const [alertas, resumen] = await Promise.all([
      obtenerAlertasStock(),
      obtenerResumenHoy(),
    ]);
    renderAlertas(alertas);
    // "Productos en alerta" se deriva de la lista: siempre consistente con ella.
    renderResumen({ ...resumen, alertas: alertas.length });
  } catch (err) {
    console.error('[inicio]', err);
    renderAlertasError('No se pudo cargar la información. Intenta de nuevo.');
  }
}

export function initInicio() {
  initAccesos();
  cargarInicio();

  // Refresca los datos cada vez que se vuelve a la sección Inicio.
  document.addEventListener('seccion:activada', (e) => {
    if (e.detail.seccion === 'inicio') cargarInicio();
  });
}                                                         
