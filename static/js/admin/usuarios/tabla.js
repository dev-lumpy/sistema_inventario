import { $, crearEl, crearFilaEstado } from '../../shared/core/dom.js';

export const SELECTOR_TBODY = '#tbody-usuarios';

const ANCHOS_COLUMNAS = ['28%', '36%', '14%', '22%'];

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

export function renderTabla(lista) {
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
    if (vendedor.solicitud) {
      tdAcciones.append(
        botonAccion({
          accion: 'aceptar',
          id: vendedor.uuid,
          icono: 'fa-check',
          texto: 'Aceptar',
        }),
        botonAccion({
          accion: 'rechazar',
          id: vendedor.uuid,
          icono: 'fa-xmark',
          texto: 'Rechazar',
        }),
      );
    } else {
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
    }

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
