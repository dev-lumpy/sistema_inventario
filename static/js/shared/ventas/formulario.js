import {
  $,
  crearEl,
  crearFilaEstado,
  limpiarSelect,
  llenarSelect,
  mostrarMensaje,
  ocultarMensaje,
} from '../core/dom.js';
import { formatearNumero, formatearPrecio } from '../core/format.js';
import { obtenerProductos, addMovimientoStock } from './api.js';

function aLista(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

let productos = [];
let carrito = [];
let monedaCarrito = null;

function productoSeleccionado(selectProducto) {
  return productos.find(
    (producto) => String(producto.id) === String(selectProducto.value),
  );
}

function itemDelCarrito(productoId) {
  return carrito.find(
    (item) => String(item.producto.id) === String(productoId),
  );
}

function totalCarrito() {
  return carrito.reduce(
    (total, item) => total + item.cantidad * Number(item.producto.precio_unitario || 0),
    0,
  );
}

function renderTabla() {
  const tbody = $('#tbody-venta');
  const totalEl = $('#venta-total');
  if (!tbody) return;

  tbody.replaceChildren();

  if (!carrito.length) {
    tbody.replaceChildren(crearFilaEstado(
      5,
      'Todavía no agregaste productos.',
      { icono: 'fa-cart-shopping' },
    ));
    if (totalEl) totalEl.textContent = '—';
    return;
  }

  for (const item of carrito) {
    const tr = document.createElement('tr');
    const cantidad = Number(item.cantidad);
    const precio = Number(item.producto.precio_unitario || 0);
    const subtotal = cantidad * precio;

    const tdAcciones = crearEl('td', { clase: 'acciones' });
    tdAcciones.appendChild(crearEl('button', {
      clase: 'btn-icon con-texto eliminar',
      texto: 'Quitar',
      attrs: {
        type: 'button',
        'data-action': 'quitar',
        'data-id': item.producto.id,
        title: 'Quitar de la venta',
      },
    }));

    tr.append(
      crearEl('td', { texto: item.producto.nombre ?? '—' }),
      crearEl('td', { texto: formatearNumero(cantidad) }),
      crearEl('td', { texto: formatearNumero(item.producto.stock_actual ?? 0) }),
      crearEl('td', {
        texto: formatearPrecio(subtotal, item.producto.moneda),
      }),
      tdAcciones,
    );
    tbody.appendChild(tr);
  }

  if (totalEl) {
    totalEl.textContent = formatearPrecio(totalCarrito(), monedaCarrito);
  }
}

function actualizarHint(selectProducto, ayudaStock) {
  if (!ayudaStock) return;
  const producto = productoSeleccionado(selectProducto);
  if (!producto) {
    ayudaStock.textContent = 'Stock disponible: —';
    return;
  }

  const enCarrito = itemDelCarrito(producto.id);
  const extra = enCarrito ? ` (en la lista: ${formatearNumero(enCarrito.cantidad)})` : '';
  ayudaStock.textContent = `Stock disponible: ${formatearNumero(producto.stock_actual ?? 0)}${extra}`;
}

function limpiarCarrito({ selectProducto, ayudaStock, mensaje } = {}) {
  carrito = [];
  monedaCarrito = null;
  renderTabla();
  if (selectProducto && ayudaStock) actualizarHint(selectProducto, ayudaStock);
  if (mensaje) ocultarMensaje(mensaje);
}

export async function cargarProductos() {
  const selectProducto = $('#venta-producto');
  if (!selectProducto) return productos;

  const seleccionado = selectProducto.value;
  productos = aLista(await obtenerProductos());

  carrito = carrito
    .map((item) => {
      const actual = productos.find(
        (producto) => String(producto.id) === String(item.producto.id),
      );
      return actual ? { ...item, producto: actual } : null;
    })
    .filter(Boolean);

  limpiarSelect(selectProducto, 'Seleccioná un producto');
  llenarSelect(selectProducto, productos);

  if (seleccionado && productos.some((p) => String(p.id) === seleccionado)) {
    selectProducto.value = seleccionado;
  }

  renderTabla();
  actualizarHint(selectProducto, $('#venta-producto-stock'));
  return productos;
}

function agregarAlCarrito({ selectProducto, inputCantidad, ayudaStock, mensaje }) {
  ocultarMensaje(mensaje);

  const producto = productoSeleccionado(selectProducto);
  const cantidad = Number(inputCantidad.value);

  if (!producto) {
    mostrarMensaje(mensaje, 'Elegí un producto.', 'error');
    return;
  }
  if (!cantidad || cantidad < 1) {
    mostrarMensaje(mensaje, 'La cantidad debe ser mayor a cero.', 'error');
    return;
  }
  if (monedaCarrito && producto.moneda !== monedaCarrito) {
    mostrarMensaje(
      mensaje,
      'No se pueden mezclar monedas en una misma venta.',
      'error',
    );
    return;
  }

  const existente = itemDelCarrito(producto.id);
  const nuevaCantidad = (existente?.cantidad ?? 0) + cantidad;
  const stock = Number(producto.stock_actual ?? 0);

  if (nuevaCantidad > stock) {
    mostrarMensaje(
      mensaje,
      `No hay stock suficiente. Disponible: ${formatearNumero(stock)}.`,
      'error',
    );
    return;
  }

  if (existente) {
    carrito = carrito.filter((item) => item !== existente);
  }
  carrito.unshift({ producto, cantidad: nuevaCantidad });
  monedaCarrito = producto.moneda;

  inputCantidad.value = '';
  renderTabla();
  actualizarHint(selectProducto, ayudaStock);
  inputCantidad.focus();
}

async function registrarVenta({
  form,
  selectProducto,
  selectCanal,
  ayudaStock,
  mensaje,
  boton,
}) {
  ocultarMensaje(mensaje);

  if (!carrito.length) {
    mostrarMensaje(mensaje, 'Agregá al menos un producto a la venta.', 'error');
    return;
  }

  const canalVenta = selectCanal.value;
  if (!canalVenta) {
    mostrarMensaje(mensaje, 'Elegí un canal de venta.', 'error');
    return;
  }

  if (boton) boton.disabled = true;

  try {
    const respuesta = await addMovimientoStock({
      items: carrito.map((item) => ({
        producto: Number(item.producto.id),
        cantidad: Number(item.cantidad),
      })),
      canal_venta: canalVenta,
    });

    for (const item of respuesta.items || []) {
      const producto = productos.find(
        (productoActual) => String(productoActual.id) === String(item.producto_id),
      );
      if (producto) producto.stock_actual = item.nuevo_stock;
    }

    carrito = [];
    monedaCarrito = null;
    form.reset();
    renderTabla();
    await cargarProductos();

    mostrarMensaje(
      mensaje,
      `Venta registrada. Total: ${formatearPrecio(respuesta.total, respuesta.moneda)}.`,
      'exito',
    );
  } catch (error) {
    mostrarMensaje(mensaje, error.message, 'error');
  } finally {
    if (boton) boton.disabled = false;
  }
}

export async function initFormulario() {
  const form = $('#form-registrar-venta');
  if (!form) return;

  const selectProducto = $('#venta-producto');
  const inputCantidad = $('#venta-cantidad');
  const selectCanal = $('#venta-canal');
  const ayudaStock = $('#venta-producto-stock');
  const mensaje = $('#venta-mensaje');
  const botonAgregar = $('#venta-agregar');
  const botonRegistrar = $('#btn-registrar-venta');
  const tbody = $('#tbody-venta');

  try {
    await cargarProductos();
  } catch (error) {
    mostrarMensaje(mensaje, `No se pudieron cargar los productos: ${error.message}`, 'error');
    return;
  }

  selectProducto?.addEventListener('change', () => {
    actualizarHint(selectProducto, ayudaStock);
  });

  botonAgregar?.addEventListener('click', () => {
    agregarAlCarrito({
      selectProducto,
      inputCantidad,
      ayudaStock,
      mensaje,
    });
  });

  tbody?.addEventListener('click', (evento) => {
    const boton = evento.target.closest('button[data-action="quitar"]');
    if (!boton) return;
    carrito = carrito.filter(
      (item) => String(item.producto.id) !== String(boton.dataset.id),
    );
    if (!carrito.length) monedaCarrito = null;
    renderTabla();
    actualizarHint(selectProducto, ayudaStock);
  });

  form.addEventListener('reset', () => {
    limpiarCarrito({ selectProducto, ayudaStock, mensaje });
  });

  form.addEventListener('submit', (evento) => {
    evento.preventDefault();
    registrarVenta({
      form,
      selectProducto,
      selectCanal,
      ayudaStock,
      mensaje,
      boton: botonRegistrar,
    });
  });

  renderTabla();
}
