import { $ } from '../../shared/core/dom.js';

const HINT_DEFAULT = 'Obligatorio, máximo 100 caracteres';

const form = $('#form-categoria');
const inputNombre = $('#categoria-nombre');
const labelStatus = $('#categoria-label-status');
const hint = $('.label-hint');
const btnCancelar = $('#btn-cancelar-categoria');

let editandoId = null;

function setLabelStatus(texto) {
  if (labelStatus) labelStatus.textContent = texto;
}

export function mostrarEstado(texto, { error = false } = {}) {
  if (!hint) return;
  hint.textContent = texto;
  hint.style.color = error ? '#c0392b' : '';
}

export function getEditandoId() {
  return editandoId;
}

export function resetFormulario() {
  editandoId = null;
  form?.reset();
  setLabelStatus('Agregar Categoría');
  if (hint) {
    hint.textContent = HINT_DEFAULT;
    hint.style.color = '';
  }
}

export function cargarCategoria(categoria) {
  editandoId = categoria.id;
  if (inputNombre) inputNombre.value = categoria.nombre;
  setLabelStatus(`Editando: ${categoria.nombre}`);
  mostrarEstado('Modificá el nombre y guardá los cambios.');
  inputNombre?.focus();
  form?.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

export function initFormulario({ onGuardar }) {
  if (!form) return;

  form.addEventListener('submit', async (evento) => {
    evento.preventDefault();

    const nombre = inputNombre.value.trim();
    if (!nombre) {
      mostrarEstado('Ingresá un nombre para la categoría.', { error: true });
      return;
    }

    const boton = form.querySelector('button[type="submit"]');
    boton.disabled = true;

    try {
      const mensaje = await onGuardar({ id: editandoId, nombre });
      resetFormulario();
      mostrarEstado(mensaje || 'Categoría guardada.');
    } catch (error) {
      mostrarEstado(error.message, { error: true });
    } finally {
      boton.disabled = false;
    }
  });

  btnCancelar?.addEventListener('click', resetFormulario);
}
