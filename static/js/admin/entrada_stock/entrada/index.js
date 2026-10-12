// static/js/admin/entrada_stock/js/entrada/index.js
import { initFormulario } from './formulario.js';
import { cargarHistorial } from './historial.js';

export async function initEntradaStock() {
  await initFormulario();
  await cargarHistorial();
}
