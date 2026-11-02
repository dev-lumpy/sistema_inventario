import { $, crearEl, crearFilaEstado } from '../../shared/core/dom.js';

const tbody = $('#tbody-categorias');

export function renderTabla(categorias) {
  if (!tbody) {
    console.log('[categoria-tabla] renderTabla: no existe #tbody-categorias');
    return;
  }

  tbody.replaceChildren();

  if (!categorias?.length) {
    console.log('[categoria-tabla] renderTabla: sin categorías');
    tbody.replaceChildren(crearFilaEstado(2, 'No hay categorías registradas.', {
      icono: 'fa-folder-open',
    }));
    return;
  }


  for (const categoria of categorias) {
    const tr = document.createElement('tr');

    const tdNombre = crearEl('td', { texto: categoria.nombre });

    const tdAcciones = crearEl('td', { clase: 'acciones' });
    tdAcciones.append(
      crearEl('button', {
        clase: 'btn-icon editar',
        attrs: {
          type: 'button',
          'data-action': 'editar',
          'data-id': categoria.id,
          title: 'Editar',
        },
      }),
      crearEl('button', {
        clase: 'btn-icon eliminar',
        attrs: {
          type: 'button',
          'data-action': 'eliminar',
          'data-id': categoria.id,
          title: 'Eliminar',
        },
      }),
    );

    tdAcciones.firstChild.appendChild(crearEl('i', { clase: 'fa-solid fa-pen' }));
    tdAcciones.lastChild.appendChild(crearEl('i', { clase: 'fa-solid fa-trash' }));

    tr.append(tdNombre, tdAcciones);
    tbody.appendChild(tr);
  }

  console.log('[categoria-tabla] renderTabla: fin');
}

export function initTabla({ onEditar, onEliminar }) {
  if (!tbody) {
    console.log('[categoria-tabla] initTabla: no existe #tbody-categorias');
    return;
  }

  tbody.addEventListener('click', (evento) => {
    const boton = evento.target.closest('button[data-action]');
    if (!boton) {
      console.log('[categoria-tabla] click sin botón de acción');
      return;
    }

    const { action, id } = boton.dataset;
    if (action === 'editar') onEditar(id);
    if (action === 'eliminar') onEliminar(id);
  });
}
