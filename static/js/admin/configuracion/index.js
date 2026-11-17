import { $, mostrarMensaje, ocultarMensaje } from '../../shared/core/dom.js';
import { actualizarPerfil, obtenerPerfil } from './api.js';

async function cargar() {
  const nombre = $('#config-nombre-negocio');
  const moneda = $('#config-moneda');
  if (!nombre || !moneda) return;

  try {
    const perfil = await obtenerPerfil();
    nombre.value = perfil.nombre_negocio ?? '';
    moneda.value = perfil.moneda ?? 'BOB';
  } catch (error) {
    mostrarMensaje($('#config-mensaje'), error.message, 'error');
  }
}

async function guardar(evento) {
  evento.preventDefault();

  const nombre = $('#config-nombre-negocio');
  const moneda = $('#config-moneda');
  const mensaje = $('#config-mensaje');
  const boton = $('#form-configuracion button[type="submit"]');

  ocultarMensaje(mensaje);
  if (boton) boton.disabled = true;

  try {
    const perfil = await actualizarPerfil({
      nombre_negocio: nombre?.value.trim() ?? '',
      moneda: moneda?.value ?? 'BOB',
    });
    window.APP_MONEDA = perfil.moneda;
    mostrarMensaje(
      mensaje,
      `Configuración guardada. Moneda actual: ${perfil.moneda}.`,
      'exito',
    );
    setTimeout(() => window.location.reload(), 1200);
  } catch (error) {
    mostrarMensaje(mensaje, error.message, 'error');
  } finally {
    if (boton) boton.disabled = false;
  }
}

export async function initConfiguracion() {
  const form = $('#form-configuracion');
  if (!form) return;

  form.addEventListener('submit', guardar);
  await cargar();

  document.addEventListener('seccion:activada', (evento) => {
    if (evento.detail?.seccion === 'configuracion') cargar();
  });
}
