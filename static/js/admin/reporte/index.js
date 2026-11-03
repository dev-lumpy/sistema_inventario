import { $, crearEl, crearFilaEstado } from '../../shared/core/dom.js';
import { ENDPOINTS } from '../../shared/core/config.js';
import { getJSON } from '../../shared/core/http.js';

const SELECTOR_TBODY = '#tbody-mas-vendidos';

function aLista(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

function isoLocal(fecha) {
  const anio = fecha.getFullYear();
  const mes = String(fecha.getMonth() + 1).padStart(2, '0');
  const dia = String(fecha.getDate()).padStart(2, '0');
  return `${anio}-${mes}-${dia}`;
}

function query(desde, hasta) {
  return `?desde=${encodeURIComponent(desde)}&hasta=${encodeURIComponent(hasta)}`;
}

function resetStats() {
  const entradas = $('#stat-total-entradas');
  const salidas = $('#stat-total-salidas');

  if (entradas) entradas.textContent = '—';
  if (salidas) salidas.textContent = '—';
}

function renderEstado(mensaje, opciones) {
  const tbody = $(SELECTOR_TBODY);
  if (!tbody) return;
  tbody.replaceChildren(crearFilaEstado(2, mensaje, opciones));
}

function renderVendidos(lista) {
  const tbody = $(SELECTOR_TBODY);
  if (!tbody) return;

  tbody.replaceChildren();

  if (!lista.length) {
    tbody.replaceChildren(crearFilaEstado(2, 'No hay ventas registradas en el período.', {
      icono: 'fa-chart-line',
    }));
    return;
  }

  for (const item of lista) {
    const tr = document.createElement('tr');
    tr.append(
      crearEl('td', { texto: item.nombre ?? '—' }),
      crearEl('td', { texto: String(item.cantidad_vendida ?? 0) }),
    );
    tbody.appendChild(tr);
  }
}

function renderResumen(resumen) {
  const entradas = $('#stat-total-entradas');
  const salidas = $('#stat-total-salidas');

  if (entradas) entradas.textContent = String(resumen?.entradas ?? 0);
  if (salidas) salidas.textContent = String(resumen?.salidas ?? 0);
}

function mostrarCargando() {
  renderEstado('Generando reporte...', { icono: 'fa-spinner fa-spin' });
  resetStats();
}

function mostrarError(texto) {
  renderEstado(texto, { icono: 'fa-triangle-exclamation', error: true });
  resetStats();
}

function nombreDesdeRespuesta(response) {
  const disposicion = response.headers.get('Content-Disposition') || '';
  const coincidencia = disposicion.match(/filename="?([^"]+)"?/i);
  return coincidencia?.[1] || '';
}

async function descargarPdf(desde, hasta) {
  const response = await fetch(`${ENDPOINTS.reportePdf}${query(desde, hasta)}`, {
    credentials: 'include',
    headers: { Accept: 'application/pdf' },
  });

  if (!response.ok) {
    let detalle = '';

    try {
      const data = await response.json();
      detalle = data?.detail || data?.error || '';
    } catch {
      detalle = '';
    }

    throw new Error(detalle || `No se pudo generar el PDF (${response.status}).`);
  }

  const blob = await response.blob();
  const nombre = nombreDesdeRespuesta(response) || `reporte_${desde}_${hasta}.pdf`;
  const url = URL.createObjectURL(blob);

  const enlace = document.createElement('a');
  enlace.href = url;
  enlace.download = nombre;
  document.body.appendChild(enlace);
  enlace.click();
  enlace.remove();

  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export async function initReporte() {
  const form = $('#form-filtros-reportes');
  if (!form) return;

  const cardMovimientos = document.querySelector('.movimientos-periodo');
  if (cardMovimientos && !cardMovimientos.classList.contains('resumen-dia')) {
    cardMovimientos.classList.add('resumen-dia');
  }

  const inputDesde = $('#reporte-desde');
  const inputHasta = $('#reporte-hasta');
  const botonGenerar = form.querySelector('button[type="submit"]');
  const botonPdf = $('#btn-exportar-pdf');

  if (inputDesde && inputHasta && !inputDesde.value && !inputHasta.value) {
    const hoy = new Date();
    inputDesde.value = isoLocal(new Date(hoy.getFullYear(), hoy.getMonth(), 1));
    inputHasta.value = isoLocal(hoy);
  }

  function deshabilitar(estado) {
    if (botonGenerar) botonGenerar.disabled = estado;
    if (botonPdf) botonPdf.disabled = estado;
  }

  async function generar() {
    const desde = inputDesde?.value;
    const hasta = inputHasta?.value;

    if (!desde || !hasta) {
      mostrarError('Elegí las fechas "Desde" y "Hasta".');
      return false;
    }

    if (desde > hasta) {
      mostrarError('La fecha "Desde" no puede ser posterior a "Hasta".');
      return false;
    }

    deshabilitar(true);
    mostrarCargando();

    try {
      const [vendidos, resumen] = await Promise.all([
        getJSON(`${ENDPOINTS.productosVendidos}${query(desde, hasta)}`),
        getJSON(`${ENDPOINTS.resumenPeriodo}${query(desde, hasta)}`),
      ]);

      renderVendidos(aLista(vendidos));
      renderResumen(resumen);
      return true;
    } catch (error) {
      mostrarError(`No se pudo generar el reporte: ${error.message}`);
      return false;
    } finally {
      deshabilitar(false);
    }
  }

  form.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    await generar();
  });

  botonPdf?.addEventListener('click', async () => {
    const desde = inputDesde?.value;
    const hasta = inputHasta?.value;

    if (!desde || !hasta) {
      return mostrarError('Elegí las fechas "Desde" y "Hasta".');
    }

    if (desde > hasta) {
      return mostrarError('La fecha "Desde" no puede ser posterior a "Hasta".');
    }

    deshabilitar(true);

    try {
      await descargarPdf(desde, hasta);
    } catch (error) {
      alert(error.message);
    } finally {
      deshabilitar(false);
    }
  });
}
