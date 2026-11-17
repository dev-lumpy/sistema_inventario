import { $, crearEl, crearFilaEstado } from '../../shared/core/dom.js';
import {
  actualizarProveedor,
  crearProveedor,
  eliminarProveedor,
  listarProveedores,
} from './api.js';

const SELECTOR_TBODY = '#tbody-proveedores';

let proveedores = [];
let inicializado = false;

function fila(proveedor) {
  const tr = document.createElement('tr');

  const tdEstado = crearEl('td');
  tdEstado.appendChild(crearEl('span', {
    clase: 'badge badge-ok',
    texto: proveedor.activo === false ? 'Inactivo' : 'Activo',
  }));

  const tdAcciones = crearEl('td', { clase: 'acciones' });
  tdAcciones.append(
    crearEl('button', {
      clase: 'btn-icon con-texto editar',
      texto: 'Editar',
      attrs: {
        type: 'button',
        'data-action': 'editar',
        'data-id': proveedor.id,
        title: 'Editar',
      },
    }),
    crearEl('button', {
      clase: 'btn-icon con-texto eliminar',
      texto: 'Eliminar',
      attrs: {
        type: 'button',
        'data-action': 'eliminar',
        'data-id': proveedor.id,
        title: 'Eliminar',
      },
    }),
  );

  tr.append(
    crearEl('td', { texto: proveedor.nombre ?? '—' }),
    crearEl('td', { texto: proveedor.contacto || '—' }),
    tdEstado,
    tdAcciones,
  );
  return tr;
}

function renderTabla() {
  const tbody = $(SELECTOR_TBODY);
  if (!tbody) return;

  tbody.replaceChildren();

  if (!proveedores.length) {
    tbody.replaceChildren(crearFilaEstado(4, 'No hay proveedores registrados.', {
      icono: 'fa-truck-field',
    }));
    return;
  }

  tbody.replaceChildren(...proveedores.map(fila));
}

async function cargar() {
  const tbody = $(SELECTOR_TBODY);
  if (!tbody) return;

  try {
    proveedores = await listarProveedores();
    renderTabla();
  } catch (error) {
    tbody.replaceChildren(crearFilaEstado(
      4,
      `No se pudieron cargar los proveedores: ${error.message}`,
      { icono: 'fa-triangle-exclamation', error: true },
    ));
  }
}

function resetFormulario() {
  $('#form-proveedor')?.reset();
  const id = $('#proveedor-id');
  if (id) id.value = '';
}

function cargarEnFormulario(proveedor) {
  const id = $('#proveedor-id');
  const nombre = $('#proveedor-nombre');
  const contacto = $('#proveedor-contacto');
  if (id) id.value = proveedor.id;
  if (nombre) nombre.value = proveedor.nombre ?? '';
  if (contacto) contacto.value = proveedor.contacto ?? '';
  nombre?.focus();
}

async function guardar(evento) {
  evento.preventDefault();

  const id = $('#proveedor-id')?.value;
  const nombre = $('#proveedor-nombre')?.value.trim();
  const contacto = $('#proveedor-contacto')?.value.trim();
  const boton = $('#form-proveedor button[type="submit"]');

  if (!nombre) {
    alert('Ingresá el nombre del proveedor.');
    return;
  }

  if (boton) boton.disabled = true;

  try {
    const payload = { nombre, contacto };
    if (id) {
      await actualizarProveedor(id, payload);
    } else {
      await crearProveedor(payload);
    }
    resetFormulario();
    await cargar();
  } catch (error) {
    alert(error.message);
  } finally {
    if (boton) boton.disabled = false;
  }
}

async function eliminar(id) {
  const proveedor = proveedores.find((item) => String(item.id) === String(id));
  if (!proveedor) return;

  if (!confirm(`¿Eliminar el proveedor "${proveedor.nombre}"?`)) return;

  try {
    await eliminarProveedor(id);
    await cargar();
  } catch (error) {
    alert(error.message);
  }
}

export async function initProveedores() {
  const form = $('#form-proveedor');
  if (!form) return;

  const tbody = $(SELECTOR_TBODY);

  if (!inicializado) {
    inicializado = true;
    form.addEventListener('submit', guardar);
    $('#btn-cancelar-proveedor')?.addEventListener('click', resetFormulario);

    tbody?.addEventListener('click', (evento) => {
      const boton = evento.target.closest('button[data-action]');
      if (!boton) return;

      const { action, id } = boton.dataset;
      if (action === 'editar') {
        const proveedor = proveedores.find(
          (item) => String(item.id) === String(id),
        );
        if (proveedor) cargarEnFormulario(proveedor);
      }
      if (action === 'eliminar') eliminar(id);
    });
  }

  await cargar();

  document.addEventListener('seccion:activada', (evento) => {
    if (evento.detail?.seccion === 'proveedores') cargar();
  });
}
