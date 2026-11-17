import { cargarCombos, initFormulario } from './formulario.js';
import { cargarHistorial } from './historial.js';

export async function initEntradaStock() {
  if (!document.getElementById('form-registrar-entrada')) return;

  await initFormulario({ onRegistrada: cargarHistorial });
  cargarHistorial();

  document.addEventListener('seccion:activada', async (evento) => {
    if (evento.detail.seccion !== 'entradas') return;
    await Promise.all([cargarCombos(), cargarHistorial()]).catch((error) => {
      console.error('[entradas] No se pudieron refrescar los datos:', error);
    });
  });
}
