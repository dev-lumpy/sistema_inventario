import { $, crearEl, crearFilaEstado } from '../../shared/core/dom.js';
import { formatearFecha } from '../../shared/core/format.js';
import {
  cancelarSolicitud,
  crearSolicitud,
  listarSolicitudes,
} from './api.js';

const COLUMNAS = 6;

function claseEstado(estado) {
  if (estado === 'aceptado') return 'badge-aceptada';
  if (estado === 'pendiente') return 'badge-pendiente';
  return 'badge-bloqueada';
}

function textoEstado(estado) {
  return String(estado || '—').charAt(0).toUpperCase() + String(estado || '').slice(1);
}

function fila(solicitud) {
  const tr = document.createElement('tr');

  const tdEstado = crearEl('td');
  tdEstado.appendChild(crearEl('span', {
    clase: `badge ${claseEstado(solicitud.estado)}`,
    texto: textoEstado(solicitud.estado),
  }));

  const tdAcciones = crearEl('td', { clase: 'acciones' });
  if (solicitud.estado === 'pendiente') {
    const boton = crearEl('button', {
      clase: 'btn-icon con-texto eliminar',
      texto: 'Cancelar',
      attrs: {
        type: 'button',
        'data-action': 'cancelar',
        'data-id': solicitud.id,
        title: 'Cancelar solicitud',
      },
    });
    tdAcciones.appendChild(boton);
  } else {
    tdAcciones.appendChild(document.createTextNode('—'));
  }

  tr.append(
    crearEl('td', { texto: solicitud.administrador?.username ?? '—' }),
    crearEl('td', { texto: solicitud.administrador?.email ?? '—' }),
    crearEl('td', { texto: solicitud.mensaje || '—' }),
    crearEl('td', { texto: formatearFecha(solicitud.fecha_creacion) }),
    tdEstado,
    tdAcciones,
  );
  return tr;
}

function render(solicitudes) {
  const tbody = $('#solicitudes-tbody');
  const vacio = $('#solicitudes-vacio');
  const wrapper = $('#solicitudes-tabla-wrapper');
  if (!tbody) return;

  tbody.replaceChildren();

  if (!solicitudes.length) {
    if (vacio) vacio.hidden = false;
    if (wrapper) wrapper.hidden = true;
    return;
  }

  if (vacio) vacio.hidden = true;
  if (wrapper) wrapper.hidden = false;
  tbody.replaceChildren(...solicitudes.map(fila));
}

function mostrarFeedback(texto, tipo = '') {
  const feedback = $('#solicitud-feedback');
  if (!feedback) return;
  feedback.textContent = texto;
  feedback.className = `form-feedback ${tipo}`.trim();
  feedback.hidden = !texto;
}

async function cargar() {
  const tbody = $('#solicitudes-tbody');
  if (!tbody) return;

  try {
    const solicitudes = await listarSolicitudes();
    render(Array.isArray(solicitudes) ? solicitudes : []);
  } catch (error) {
    tbody.replaceChildren(crearFilaEstado(COLUMNAS, error.message, {
      icono: 'fa-triangle-exclamation',
      error: true,
    }));
    const wrapper = $('#solicitudes-tabla-wrapper');
    if (wrapper) wrapper.hidden = false;
  }
}

async function enviar(evento) {
  evento.preventDefault();

  const email = $('#solicitud-email')?.value.trim();
  const mensaje = $('#solicitud-mensaje')?.value.trim();
  const boton = $('#btn-enviar-solicitud');

  if (!email) {
    mostrarFeedback('Ingresá el email del administrador.', 'error');
    return;
  }

  if (boton) boton.disabled = true;

  try {
    await crearSolicitud({
      email_administrador: email,
      mensaje,
    });
    mostrarFeedback('Solicitud enviada. Esperá la respuesta del administrador.');
    $('#form-solicitud-admin')?.reset();
    await cargar();
  } catch (error) {
    mostrarFeedback(error.message, 'error');
  } finally {
    if (boton) boton.disabled = false;
  }
}

async function cancelar(id) {
  if (!confirm('¿Cancelar esta solicitud?')) return;

  try {
    await cancelarSolicitud(id);
    mostrarFeedback('Solicitud cancelada.');
    await cargar();
  } catch (error) {
    mostrarFeedback(error.message, 'error');
  }
}

export async function initSolicitudes() {
  const form = $('#form-solicitud-admin');
  if (!form) return;

  form.addEventListener('submit', enviar);

  $('#solicitudes-tbody')?.addEventListener('click', (evento) => {
    const boton = evento.target.closest('button[data-action="cancelar"]');
    if (!boton) return;
    cancelar(boton.dataset.id);
  });

  await cargar();

  document.addEventListener('seccion:activada', (evento) => {
    if (evento.detail?.seccion === 'solicitudes-admin') cargar();
  });
}
