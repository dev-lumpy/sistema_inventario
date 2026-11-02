import { initFormulario } from './formulario.js';

export async function initVentas() {
  if (!document.getElementById('form-registrar-venta')) return;
  await initFormulario();
}
