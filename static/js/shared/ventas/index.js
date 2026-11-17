import { cargarProductos, initFormulario } from './formulario.js';

export async function initVentas() {
  if (!document.getElementById('form-registrar-venta')) return;
  await initFormulario();

  document.addEventListener('seccion:activada', (evento) => {
    if (evento.detail?.seccion !== 'ventas') return;
    cargarProductos().catch((error) => {
      console.error('[ventas] No se pudieron refrescar los productos:', error);
    });
  });
}
