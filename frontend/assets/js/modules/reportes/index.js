/**
 * Módulo Reportes
 * ----------------
 * Orquestador del dashboard de reportes
 *
 * RESPONSABILIDADES:
 * - Inicializar navegación interna (tabs)
 * - Inicializar filtros (fechas + agrupación)
 * - Pedir datos al backend
 * - Renderizar SOLO la vista activa
 *
 * NO:
 * - Lógica de negocio
 * - Render de gráficas
 */

import { generarReporte } from '../../api.js';
import { mostrarTabReporte, marcarTabReporte } from '../../router.js';

import { renderGeneral } from './general.js';
import { renderPasillos } from './pasillos.js';
import { renderPersonas } from './personas.js';
import { renderZonas } from './zonas.js';
import { renderDetalle } from './detalle.js';

/* ======================================================
   ESTADO LOCAL (única fuente de verdad)
====================================================== */
let resultadoActual = null;
let tabActiva = 'general';
let filtrosActuales = null;

/* ======================================================
   ENTRY POINT
====================================================== */
export function cargarReportes() {
  console.log('🟢 cargarReportes()');

  filtrosActuales = _filtrosPorDefecto();

  _initTabs();
  _initFiltros();
  _initEventosGlobales();

  _actualizar();
}

/* ======================================================
   Tabs internas
====================================================== */
function _initTabs() {
  const buttons = document.querySelectorAll('[data-tab]');
  if (!buttons.length) return;

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
      if (!tab || tab === tabActiva) return;

      tabActiva = tab;
      mostrarTabReporte(tabActiva);
      marcarTabReporte(tabActiva);
      _renderTabActiva();
    });
  });

  mostrarTabReporte(tabActiva);
  marcarTabReporte(tabActiva);
}

/* ======================================================
   Filtros (fechas + agrupar)
====================================================== */
function _initFiltros() {
  const container = document.getElementById('filters-container');
  if (!container) return;

  container.innerHTML = `
    <form id="reportes-filters" class="filters-form">

      <label>
        Desde
        <input type="date" name="desde">
      </label>

      <label>
        Hasta
        <input type="date" name="hasta">
      </label>

      <label>
        Agrupar por
        <select name="agrupar" id="agrupar-select">
          <option value="Dia">Día</option>
          <option value="Semana">Semana</option>
          <option value="Mes">Mes</option>
          <option value="Anio">Año</option>
        </select>
      </label>

      <button type="submit">Generar</button>
    </form>
  `;

  const form = container.querySelector('#reportes-filters');
  const agruparSelect = container.querySelector('#agrupar-select');

  // Inicializar valores
  form.desde.value = filtrosActuales.desde;
  form.hasta.value = filtrosActuales.hasta;
  agruparSelect.value = filtrosActuales.agrupar;

  // 👉 Submit manual
  form.addEventListener('submit', e => {
    e.preventDefault();
    _actualizarDesdeFormulario(form);
  });

  // 👉 Cambio inmediato de agrupación
  agruparSelect.addEventListener('change', e => {
    filtrosActuales = {
      ...filtrosActuales,
      agrupar: e.target.value
    };
    _actualizar();
  });
}

/* ======================================================
   Eventos globales desde vistas (GeneralView)
====================================================== */
function _initEventosGlobales() {
  window.addEventListener('cambiar-agrupacion', e => {
    const agrupar = e.detail?.agrupar;
    if (!agrupar || agrupar === filtrosActuales.agrupar) return;

    filtrosActuales = {
      ...filtrosActuales,
      agrupar
    };

    _actualizar();
  });
}

/* ======================================================
   Filtros por defecto
====================================================== */
function _filtrosPorDefecto() {
  const hoy = new Date();
  const desde = new Date(hoy.getFullYear(), hoy.getMonth(), 1);

  return {
    desde: desde.toISOString().slice(0, 10),
    hasta: hoy.toISOString().slice(0, 10),
    agrupar: 'Mes'
  };
}

/* ======================================================
   Actualizar reportes (API)
====================================================== */
async function _actualizar() {
  console.log('🟡 Actualizando reportes', filtrosActuales);

  try {
    resultadoActual = await generarReporte(filtrosActuales);
  } catch (err) {
    console.error('❌ Error al generar reportes', err);
    return;
  }

  if (!resultadoActual) return;

  _renderTabActiva();
}

/* ======================================================
   Leer filtros desde formulario
====================================================== */
function _actualizarDesdeFormulario(form) {
  filtrosActuales = {
    ...filtrosActuales,
    ...Object.fromEntries(new FormData(form))
  };
  _actualizar();
}

/* ======================================================
   Render SOLO pestaña activa
====================================================== */
function _renderTabActiva() {
  if (!resultadoActual) return;

  console.log(`🟣 Render tab activa: ${tabActiva}`);

  switch (tabActiva) {
    case 'general':
      renderGeneral(resultadoActual);
      break;
    case 'pasillos':
      renderPasillos(resultadoActual);
      break;
    case 'personas':
      renderPersonas(resultadoActual);
      break;
    case 'zonas':
      renderZonas(resultadoActual);
      break;
    case 'detalle':
      renderDetalle(resultadoActual);
      break;
  }
}
