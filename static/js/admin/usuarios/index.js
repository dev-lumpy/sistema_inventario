import { $, crearEl, crearFilaEstado } from '../../shared/core/dom.js';
import { CONFIG } from '../../shared/core/config.js';
import { deleteJSON, getJSON, patchJSON } from '../../shared/core/http.js';

const SELECTOR_TBODY = '#tbody-usuarios';
const ANCHOS_COLUMNAS = ['28%', '36%', '14%', '22%'];

let vendedores = [];
let inicializado = false;

function aLista(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

function idDelUsuarioActual() {
  return document.body.dataset.userId || '';
}

function urlVendedores(adminId) {
  return `${CONFIG.USUARIOS}/get_user/admin/${adminId}/vendedores/`;
}

function urlUsuario(uuid) {
  return `${CONFIG.USUARIOS}/api/${uuid}/`;
}

function prepararColumnas(tabla) {
  if (tabla.querySelector('colgroup')) return;

  const colgroup = crearEl('colgroup');
  for (const ancho of ANCHOS_COLUMNAS) {
    const col = crearEl('col');
    col.style.width = ancho;
    colgroup.appendChild(col);
  }
  tabla.prepend(colgroup);
}

function prepararTabla(tabla) {
  if (!tabla) return;

  if (!tabla.parentElement?.classList.contains('tabla-wrap')) {
    const wrap = crearEl('div', { clase: 'tabla-wrap' });
    tabla.parentNode.insertBefore(wrap, tabla);
    wrap.appendChild(tabla);
  }

  prepararColumnas(tabla);
}

function badgeEstado(valor) {
  const estado = String(valor ?? '').toLowerCase();
  const esActivo = estado === 'activo';
  const texto = estado
    ? estado.charAt(0).toUpperCase() + estado.slice(1)
    : '—';

  return crearEl('span', {
    clase: `badge ${esActivo ? 'badge-ok' : 'badge-bajo'}`,
    texto,
  });
}

function botonAccion({ accion, id, icono, texto }) {
  const boton = crearEl('button', {
    clase: `btn-icon con-texto ${accion}`,
    attrs: {
      type: 'button',
      'data-action': accion,
      'data-id': id,
      title: texto,
    },
  });

  boton.append(
    crearEl('i', { clase: `fa-solid ${icono}` }),
    crearEl('span', { texto }),
  );

  return boton;
}

function renderTabla(lista) {
  const tbody = $(SELECTOR_TBODY);
  if (!tbody) return;

  const tabla = tbody.closest('table');
  prepararTabla(tabla);

  tbody.replaceChildren();

  if (!lista.length) {
    tbody.replaceChildren(crearFilaEstado(4, 'No hay usuarios registrados.', {
      icono: 'fa-users',
    }));
    return;
  }

  for (const vendedor of lista) {
    const tdEstado = crearEl('td');
    tdEstado.appendChild(badgeEstado(vendedor.activo));

    const tdAcciones = crearEl('td', { clase: 'acciones' });
    tdAcciones.append(
      botonAccion({
        accion: 'editar',
        id: vendedor.uuid,
        icono: 'fa-pen',
        texto: 'Editar',
      }),
      botonAccion({
        accion: 'eliminar',
        id: vendedor.uuid,
        icono: 'fa-trash',
        texto: 'Eliminar',
      }),
    );

    const tr = document.createElement('tr');
    tr.append(
      crearEl('td', { texto: vendedor.username ?? '—' }),
      crearEl('td', { texto: vendedor.email ?? '—' }),
      tdEstado,
      tdAcciones,
    );

    tbody.appendChild(tr);
  }
}

function buscarPorId(id) {
  return vendedores.find((vendedor) => String(vendedor.uuid) === String(id));
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
    vendedores = aLista(await getJSON(urlVendedores(adminId)));
    renderTabla(vendedores);
  } catch (error) {
    tbody.replaceChildren(crearFilaEstado(
      4,
      `No se pudieron cargar los usuarios: ${error.message}`,
      { icono: 'fa-triangle-exclamation', error: true },
    ));
  }
}

function cerrarEditor() {
  document.getElementById('usuario-editor')?.remove();
}

function campo({ id, etiqueta, tipo, valor, maxlength }) {
  const grupo = crearEl('div', { clase: 'form-group' });
  const input = crearEl('input', {
    attrs: {
      id,
      type: tipo,
      value: valor ?? '',
      ...(maxlength ? { maxlength } : {}),
    },
  });

  grupo.append(
    crearEl('label', { texto: etiqueta, attrs: { for: id } }),
    input,
  );

  return { grupo, input };
}

function abrirEditor(vendedor) {
  cerrarEditor();

  const overlay = crearEl('div', { attrs: { id: 'usuario-editor' } });
  overlay.style.cssText = 'position:fixed;inset:0;z-index:2000;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.6);padding:20px;';

  const card = crearEl('div', { clase: 'card' });
  card.style.cssText = 'width:100%;max-width:420px;margin:0;';

  const body = crearEl('div', { clase: 'card-body' });
  const form = crearEl('form', { clase: 'form' });
  form.style.gridTemplateColumns = '1fr';

  const usuario = campo({
    id: 'editor-username',
    etiqueta: 'Nombre de usuario',
    tipo: 'text',
    valor: vendedor.username,
    maxlength: '150',
  });
  const email = campo({
    id: 'editor-email',
    etiqueta: 'Email',
    tipo: 'email',
    valor: vendedor.email,
  });

  const grupoActivo = crearEl('div', { clase: 'form-group' });
  const selectActivo = crearEl('select', { attrs: { id: 'editor-activo' } });
  for (const estado of ['activo', 'inactivo', 'pendiente']) {
    selectActivo.appendChild(crearEl('option', {
      texto: estado,
      attrs: { value: estado },
    }));
  }
  selectActivo.value = vendedor.activo ?? 'activo';
  grupoActivo.append(
    crearEl('label', { texto: 'Estado', attrs: { for: 'editor-activo' } }),
    selectActivo,
  );

  const error = crearEl('p', { clase: 'form-help error' });
  error.hidden = true;

  const acciones = crearEl('div', { clase: 'form-actions' });
  const btnGuardar = crearEl('button', {
    clase: 'btn btn-primario',
    attrs: { type: 'submit' },
  });
  btnGuardar.append(
    crearEl('i', { clase: 'fa-solid fa-check' }),
    crearEl('span', { texto: 'Guardar' }),
  );
  const btnCancelar = crearEl('button', {
    clase: 'btn btn-secundario',
    attrs: { type: 'button' },
  });
  btnCancelar.appendChild(document.createTextNode('Cancelar'));

  acciones.append(btnGuardar, btnCancelar);
  form.append(usuario.grupo, email.grupo, grupoActivo, error, acciones);
  body.appendChild(form);
  card.appendChild(body);
  overlay.appendChild(card);
  document.body.appendChild(overlay);

  usuario.input.focus();

  btnCancelar.addEventListener('click', cerrarEditor);
  overlay.addEventListener('click', (evento) => {
    if (evento.target === overlay) cerrarEditor();
  });

  form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    error.hidden = true;

    const payload = {
      username: usuario.input.value.trim(),
      email: email.input.value.trim(),
      activo: selectActivo.value,
    };

    btnGuardar.disabled = true;

    try {
      const actualizado = await patchJSON(urlUsuario(vendedor.uuid), payload);
      vendedores = vendedores.map((item) => (
        String(item.uuid) === String(vendedor.uuid)
          ? { ...item, ...actualizado }
          : item
      ));
      renderTabla(vendedores);
      cerrarEditor();
    } catch (err) {
      error.textContent = err.message;
      error.hidden = false;
    } finally {
      btnGuardar.disabled = false;
    }
  });
}

async function eliminar(vendedor) {
  if (!confirm(`¿Eliminar al vendedor "${vendedor.username}"?`)) return;

  try {
    await deleteJSON(urlUsuario(vendedor.uuid));
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
        abrirEditor(vendedor);
        return;
      }

      if (onEliminar) return onEliminar(vendedor);
      eliminar(vendedor);
    });
  }

  await cargar();
}
