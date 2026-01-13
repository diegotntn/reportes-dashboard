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
// (registran listeners globales)
// ─────────────────────────────

// ⛔ Vistas legacy (siguen usando eventos globales)
import './general.js';
import './pasillos.js';
import './zonas.js';
import './detalle.js';

// ✅ Personas (nueva arquitectura)
import { cargarResultadoPersonas } from './personas/index.js';

// Infraestructura
import { generarReporte } from '../api.js';
import { iniciarTabsReportes } from '../router.js';

/* ======================================================
   ESTADO ÚNICO (fuente de verdad del dashboard)
====================================================== */
let resultadoActual = null;
let filtrosActuales = null;
let inicializado = false;

// 🔒 Candado de concurrencia
let cargando = false;

/* ======================================================
   ENTRY POINT
====================================================== */
export function renderReportesScreen(container) {
  console.group('🟢 ReportesScreen init');

  // Estado inicial
  filtrosActuales = filtrosPorDefecto();

  // HTML base (SE MONTA UNA SOLA VEZ)
  container.innerHTML = `
    <section class="card reportes-screen">

      <header class="screen-header">
        <h2>Reportes</h2>
      </header>

      <!-- Filtros -->
      <section id="filters-container"></section>

      <!-- Tabs -->
      <nav class="tabs">
        <button data-tab="general" class="active">General</button>
        <button data-tab="pasillos">Pasillos</button>
        <button data-tab="personas">Personas</button>
        <button data-tab="zonas">Zonas</button>
        <button data-tab="detalle">Detalle</button>
      </nav>

      <!-- Paneles -->
      <section id="tab-general" class="tab-panel"></section>
      <section id="tab-pasillos" class="tab-panel" style="display:none"></section>
      <section id="tab-personas" class="tab-panel" style="display:none"></section>
      <section id="tab-zonas" class="tab-panel" style="display:none"></section>
      <section id="tab-detalle" class="tab-panel" style="display:none"></section>

    </section>
  `;

  console.log('📦 DOM base de Reportes creado');

  // Inicializaciones
  initFiltros();
  initEventosGlobales();

  // Router de tabs (solo visibilidad)
  iniciarTabsReportes('general');

  // Fetch inicial (UNA sola vez)
  if (!inicializado) {
    inicializado = true;
    actualizarReportes();
    console.log('📡 Fetch inicial de reportes');
  }

  console.groupEnd();
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

  // Valores iniciales
  form.desde.value = filtrosActuales.desde;
  form.hasta.value = filtrosActuales.hasta;
  form.agrupar.value = filtrosActuales.agrupar;

  // Submit explícito
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
  // Cambio de agrupación disparado por vistas legacy
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
   API (fetch + distribución de resultados)
====================================================== */
async function actualizarReportes() {
  if (cargando) {
    console.warn('⏸️ Reportes en carga, se ignora llamada duplicada');
    return;
  }

  cargando = true;

  try {
    resultadoActual = await generarReporte(filtrosActuales);
    if (!resultadoActual) return;

    // 🔔 Vistas legacy (event-driven)
    window.dispatchEvent(
      new CustomEvent('reportes:actualizados', {
        detail: resultadoActual
      })
    );

    // ✅ Personas (API directa, arquitectura nueva)
    cargarResultadoPersonas(resultadoActual);

  } catch (err) {
    console.error('❌ Error al generar reportes', err);

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
   ACCESO CONTROLADO AL ESTADO (solo lectura)
====================================================== */
export function getResultadoActual() {
  return resultadoActual;
}
