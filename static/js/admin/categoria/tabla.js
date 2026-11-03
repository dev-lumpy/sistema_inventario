import { $, crearEl, crearFilaEstado } from '../../shared/core/dom.js';

const tbody = $('#tbody-categorias');

export function renderTabla(categorias) {
  if (!tbody) {
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

    const botonEditar = crearEl('button', {
      clase: 'btn-icon con-texto editar',
      attrs: {
        type: 'button',
        'data-action': 'editar',
        'data-id': categoria.id,
        title: 'Editar',
      },
    });
    botonEditar.append(
      crearEl('i', { clase: 'fa-solid fa-pen' }),
      crearEl('span', { texto: 'Editar' }),
    );

    const botonEliminar = crearEl('button', {
      clase: 'btn-icon con-texto eliminar',
      attrs: {
        type: 'button',
        'data-action': 'eliminar',
        'data-id': categoria.id,
        title: 'Borrar',
      },
    });
    botonEliminar.append(
      crearEl('i', { clase: 'fa-solid fa-trash' }),
      crearEl('span', { texto: 'Borrar' }),
    );

    tdAcciones.append(botonEditar, botonEliminar);

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
