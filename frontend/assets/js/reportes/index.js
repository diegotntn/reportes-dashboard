/**
 * ReportesScreen
 * --------------
 * Orquestador del dashboard de reportes
 *
 * RESPONSABILIDADES:
 * - Renderizar estructura base del dashboard
 * - Inicializar filtros
 * - Pedir datos al backend
 * - Distribuir resultados a las vistas
 *
 * NO HACE:
 * - Render de gráficas
 * - Lógica interna de cada vista
 */

// ─────────────────────────────
// IMPORTS DE VISTAS
// ─────────────────────────────

// Vistas legacy (event-driven)
import './general.js';
import './pasillos.js';
import './zonas.js';
import './detalle.js';

// Personas (arquitectura nueva)
import { cargarResultadoPersonas } from './personas/index.js';

// Infraestructura
import { generarReporte } from '../api.js';
import { iniciarTabsReportes } from '../router.js';

/* ======================================================
   ESTADO ÚNICO (fuente de verdad)
====================================================== */
let resultadoActual = null;
let filtrosActuales = null;
let inicializado = false;

// Candado de concurrencia
let cargando = false;

/* ======================================================
   ENTRY POINT
====================================================== */
export function renderReportesScreen(container) {
  filtrosActuales = filtrosPorDefecto();

  // HTML base (se monta una sola vez)
  container.innerHTML = `
    <section class="card reportes-screen">

      <header class="screen-header">
        <h2>Reportes</h2>
      </header>

      <section id="filters-container"></section>

      <nav class="tabs">
        <button data-tab="general" class="active">General</button>
        <button data-tab="pasillos">Pasillos</button>
        <button data-tab="personas">Personas</button>
        <button data-tab="zonas">Zonas</button>
        <button data-tab="detalle">Detalle</button>
      </nav>

      <section id="tab-general" class="tab-panel"></section>
      <section id="tab-pasillos" class="tab-panel" style="display:none"></section>
      <section id="tab-personas" class="tab-panel" style="display:none"></section>
      <section id="tab-zonas" class="tab-panel" style="display:none"></section>
      <section id="tab-detalle" class="tab-panel" style="display:none"></section>

    </section>
  `;

  initFiltros();
  initEventosGlobales();

  iniciarTabsReportes('general');

  if (!inicializado) {
    inicializado = true;
    actualizarReportes();
  }
}

/* ======================================================
   FILTROS
====================================================== */
function initFiltros() {
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
        <select name="agrupar">
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

  form.desde.value = filtrosActuales.desde;
  form.hasta.value = filtrosActuales.hasta;
  form.agrupar.value = filtrosActuales.agrupar;

  form.addEventListener('submit', e => {
    e.preventDefault();

    filtrosActuales = {
      ...filtrosActuales,
      ...Object.fromEntries(new FormData(form))
    };

    actualizarReportes();
  });
}

/* ======================================================
   EVENTOS GLOBALES
====================================================== */
function initEventosGlobales() {
  window.addEventListener('reportes:cambiar-agrupacion', e => {
    const agrupar = e.detail?.agrupar;
    if (!agrupar || agrupar === filtrosActuales.agrupar) return;

    filtrosActuales = {
      ...filtrosActuales,
      agrupar
    };

    actualizarReportes();
  });
}

/* ======================================================
   API (fetch + distribución)
====================================================== */
async function actualizarReportes() {
  if (cargando) return;

  cargando = true;

  try {
    resultadoActual = await generarReporte(filtrosActuales);
    if (!resultadoActual) return;

    // Vistas legacy
    window.dispatchEvent(
      new CustomEvent('reportes:actualizados', {
        detail: resultadoActual
      })
    );

    // Personas
    cargarResultadoPersonas(resultadoActual);

  } finally {
    cargando = false;
  }
}

/* ======================================================
   FILTROS POR DEFECTO
====================================================== */
function filtrosPorDefecto() {
  const hoy = new Date();
  const desde = new Date(hoy.getFullYear(), hoy.getMonth(), 1);

  return {
    desde: desde.toISOString().slice(0, 10),
    hasta: hoy.toISOString().slice(0, 10),
    agrupar: 'Mes'
  };
}

/* ======================================================
   ACCESO SOLO LECTURA AL ESTADO
====================================================== */
export function getResultadoActual() {
  return resultadoActual;
}
