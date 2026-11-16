import { crearEl } from '../../shared/core/dom.js';
import { esPasswordValida, generarPasswordTemporal } from './password.js';
import { nombreAdminActual } from './utilidades.js';

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

export function abrirEditor({ vendedor = null, onGuardar }) {
  const esCreacion = !vendedor;
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
    etiqueta: esCreacion ? 'Nombre' : 'Nombre de usuario',
    tipo: 'text',
    valor: vendedor?.username,
    maxlength: '150',
  });
  const email = campo({
    id: 'editor-email',
    etiqueta: 'Email',
    tipo: 'email',
    valor: vendedor?.email,
  });

  const grupoActivo = crearEl('div', { clase: 'form-group' });
  const selectActivo = crearEl('select', { attrs: { id: 'editor-activo' } });
  for (const estado of ['activo', 'inactivo', 'pendiente']) {
    selectActivo.appendChild(crearEl('option', {
      texto: estado,
      attrs: { value: estado },
    }));
  }
  selectActivo.value = vendedor?.activo ?? 'activo';
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
    crearEl('span', { texto: esCreacion ? 'Crear' : 'Guardar' }),
  );
  const btnCancelar = crearEl('button', {
    clase: 'btn btn-secundario',
    attrs: { type: 'button' },
  });
  btnCancelar.appendChild(document.createTextNode('Cancelar'));

  acciones.append(btnGuardar, btnCancelar);
  form.append(
    usuario.grupo,
    email.grupo,
    grupoActivo,
    ...(esCreacion
      ? [crearEl('p', {
        clase: 'form-help',
        texto: 'Se generará una contraseña temporal para el usuario.',
      })]
      : []),
    error,
    acciones,
  );
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

    const nombre = usuario.input.value.trim();
    const emailValor = email.input.value.trim();
    const estado = selectActivo.value;

    btnGuardar.disabled = true;

    try {
      let adminUsername = null;
      let password = null;

      if (esCreacion) {
        if (!nombre || !emailValor) {
          throw new Error('Completá nombre y email.');
        }
        if (!/^[^\s@]+@gmail\.com$/i.test(emailValor)) {
          throw new Error('Ingresá un correo de Gmail válido.');
        }
        adminUsername = nombreAdminActual();
        if (!adminUsername) {
          throw new Error('No se pudo identificar al administrador.');
        }
        password = generarPasswordTemporal();
      }

      const mensaje = await onGuardar({
        esCreacion,
        vendedor,
        nombre,
        email: emailValor,
        estado,
        password,
        adminUsername,
      });

      cerrarEditor();
      if (mensaje) alert(mensaje);
    } catch (err) {
      error.textContent = err.message;
      error.hidden = false;
    } finally {
      btnGuardar.disabled = false;
    }
  });
}
