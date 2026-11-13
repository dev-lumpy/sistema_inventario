import { getMovimientos } from './api.js';
import { renderHistorial } from './tabla.js';

export async function initHistorial() {
  if (!document.getElementById('historial')) return;

  const cargar = async () => {
    try {
      const movimientos = await getMovimientos();
      renderHistorial(movimientos);
    } catch (error) {
      console.error('[historial]', error);
      renderHistorial([], {
        error: `No se pudo cargar el historial: ${error.message}`,
      });
    }
  };

  document.addEventListener('seccion:activada', (evento) => {
    if (evento.detail?.seccion === 'historial') cargar();
  });

  await cargar();
}
