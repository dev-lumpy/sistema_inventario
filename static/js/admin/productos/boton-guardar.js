import { $ } from '../../shared/core/dom.js';

const btnGuardar = $('#btn-guardar-producto');
const icoCheck = $('#btn-icono-check');
const icoSpin = $('#btn-icono-spinner');
const texto = $('#btn-texto');

const ESTADOS = {
  DEFAULT: { check: false, spinner: false, texto: 'Guardar' },
  CARGANDO: { check: false, spinner: true, texto: 'Guardando...' },
  CARGADO: { check: true, spinner: false, texto: 'Guardado' },
};

function aplicar(estado) {
  if (!btnGuardar || !icoCheck || !icoSpin || !texto) return;

  const config = ESTADOS[estado] || ESTADOS.DEFAULT;
  icoCheck.style.display = config.check ? 'inline-block' : 'none';
  icoSpin.style.display = config.spinner ? 'inline-block' : 'none';
  texto.textContent = config.texto;
}

export function cambiarEstadoBoton(estado) {
  aplicar(estado);
}

export function bloquearBoton(estaBloqueado) {
  if (!btnGuardar) return;
  btnGuardar.classList.toggle('loading', estaBloqueado);
  btnGuardar.disabled = estaBloqueado;
}

export function iniciarBoton() {
  aplicar('DEFAULT');
}
