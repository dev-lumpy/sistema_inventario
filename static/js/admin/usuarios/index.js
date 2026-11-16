/*
usuarios/
├── api.js          # endpoints HTTP (crear, listar, actualizar, eliminar)
├── password.js     # esPasswordValida + generarPasswordTemporal
├── utilidades.js   # aLista, idDelUsuarioActual, nombreAdminActual
├── tabla.js        # renderTabla, badges, botones, colgroup
├── formulario.js   # modal crear/editar + validación (antes vacío)
└── index.js        # estado, carga, guardar/eliminar, initUsuarios
*/
import { $, crearFilaEstado } from '../../shared/core/dom.js';
import {
  actualizarUsuario,
  crearVendedor,
  eliminarUsuario,
  listarSolicitudes,
  listarVendedores,
} from './api.js';
import { SELECTOR_TBODY, renderTabla } from './tabla.js';
import { abrirEditor } from './formulario.js';
import { aLista, idDelUsuarioActual } from './utilidades.js';

let vendedores = [];
let inicializado = false;

function buscarPorId(id) {
  return vendedores.find((vendedor) => String(vendedor.uuid) === String(id));
}

function filaSolicitud(solicitud) {
  return {
    uuid: solicitud.id,
    username: solicitud.vendedor?.username ?? '—',
    email: solicitud.vendedor?.email ?? '—',
    activo: solicitud.estado,
    solicitud: true,
    mensaje: solicitud.mensaje,
  };
}

function reemplazarVendedor(uuid, cambios) {
  vendedores = vendedores.map((item) => (
    String(item.uuid) === String(uuid)
      ? { ...item, ...cambios }
      : item
  ));
  renderTabla(vendedores);
}

async function guardar({
  esCreacion,
  vendedor,
  nombre,
  email,
  estado,
  password,
  adminUsername,
}) {
  if (!esCreacion) {
    const actualizado = await actualizarUsuario(vendedor.uuid, {
      username: nombre,
      email,
      activo: estado,
    });
    reemplazarVendedor(vendedor.uuid, actualizado);
    return null;
  }

  await crearVendedor({
    nombre,
    email,
    password,
    username: adminUsername,
  });

  await cargar();

  if (estado !== 'activo') {
    const nuevo = vendedores.find(
      (item) => (
        !item.solicitud
        && (
          String(item.email) === email
          || String(item.username) === nombre
        )
      ),
    );
    if (nuevo) {
      const actualizado = await actualizarUsuario(nuevo.uuid, { activo: estado });
      reemplazarVendedor(nuevo.uuid, actualizado);
    }
  }

  return `Usuario creado. Contraseña temporal: ${password}`;
}

async function cargar() {
  const tbody = $(SELECTOR_TBODY);
  if (!tbody) return;

  const adminId = idDelUsuarioActual();

  if (!adminId) {
    tbody.replaceChildren(crearFilaEstado(
      4,
      'No se pudo identificar al administrador.',
      { icono: 'fa-triangle-exclamation', error: true },
    ));
    return;
  }

  try {
    const [dataSolicitudes, dataVendedores] = await Promise.all([
      listarSolicitudes(adminId).catch(() => []),
      listarVendedores(adminId),
    ]);
    const solicitudes = aLista(dataSolicitudes).map(filaSolicitud);
    vendedores = [...solicitudes, ...aLista(dataVendedores)];
      console.log("[usuarios] vendedores: ", vendedores);
    renderTabla(vendedores);
  } catch (error) {
    tbody.replaceChildren(crearFilaEstado(
      4,
      `No se pudieron cargar los usuarios: ${error.message}`,
      { icono: 'fa-triangle-exclamation', error: true },
    ));
  }
}

async function eliminar(vendedor) {
  if (!confirm(`¿Eliminar al vendedor "${vendedor.username}"?`)) return;

  try {
    await eliminarUsuario(vendedor.uuid);
    vendedores = vendedores.filter(
      (item) => String(item.uuid) !== String(vendedor.uuid),
    );
    renderTabla(vendedores);
  } catch (err) {
    alert(err.message);
  }
}

export async function initUsuarios({ onEditar, onEliminar } = {}) {
  const tbody = $(SELECTOR_TBODY);
  if (!tbody) return;

  if (!inicializado) {
    inicializado = true;

    tbody.addEventListener('click', (evento) => {
      const boton = evento.target.closest('button[data-action]');
      if (!boton) return;

      const vendedor = buscarPorId(boton.dataset.id);
      if (!vendedor) return;

      if (boton.dataset.action === 'editar') {
        if (onEditar) return onEditar(vendedor);
        abrirEditor({ vendedor, onGuardar: guardar });
        return;
      }

      if (onEliminar) return onEliminar(vendedor);
      eliminar(vendedor);
    });

    $('#btn-crear-usuario')?.addEventListener('click', () => {
      abrirEditor({ onGuardar: guardar });
    });
  }

  await cargar();
}
