 /* boton-guardar.js — Apariencia del botón "Guardar" (spinner / check / texto) */

import { $ } from './utils.js';

const BLOQUEO_MS = 1500; // cada estado se muestra como mínimo este tiempo

const btnGuardar = $('btn-guardar-producto');
const icoCheck = $('btn-icono-check');
const icoSpin = $('btn-icono-spinner');
const texto = $('btn-texto');

const ESTADOS = {
  DEFAULT:  { check: false, spinner: false, texto: 'Guardar' },
  CARGANDO: { check: false, spinner: true,  texto: 'Guardando...' },
  CARGADO:  { check: true,  spinner: false, texto: 'Guardado' },
};

function aplicar(estado) {
  const cfg = ESTADOS[estado] || { check: false, spinner: false, texto: estado };
  icoCheck.style.display = cfg.check ? 'inline-block' : 'none';
  icoSpin.style.display = cfg.spinner ? 'inline-block' : 'none';
  texto.textContent = cfg.texto;
}

let bloqueado = false;
let pendiente = null; // si llega otro estado mientras está bloqueado, queda en cola

export function cambiarEstadoBoton(estado) {
  if (bloqueado) {
    pendiente = estado;
    return;
  }

  aplicar(estado);
  bloqueado = true;

  setTimeout(() => {
    bloqueado = false;
    if (pendiente !== null) {
      const siguiente = pendiente;
      pendiente = null;
      cambiarEstadoBoton(siguiente);
    }
  }, BLOQUEO_MS);
}

export function bloquearBoton(estaBloqueado) {
  btnGuardar.classList.toggle('loading', estaBloqueado);
  btnGuardar.disabled = estaBloqueado;
}

export function iniciarBoton() {
  aplicar('DEFAULT');
}
