import { initFormulario } from './formulario.js';
import { cargarHistorial } from './historial.js';

export async function initEntradaStock() {
  if (!document.getElementById('form-registrar-entrada')) return;

  await initFormulario({ onRegistrada: cargarHistorial });
  cargarHistorial();

  document.addEventListener('seccion:activada', (evento) => {
    if (evento.detail.seccion === 'entradas') cargarHistorial();
  });
}
