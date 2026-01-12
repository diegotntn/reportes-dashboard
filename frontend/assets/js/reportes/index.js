/**
 * ReportesScreen
 * --------------
 * Orquestador del dashboard de reportes
 *
 * RESPONSABILIDADES:
 * - Renderizar estructura base del dashboard
 * - Inicializar filtros
 * - Pedir datos al backend
 * - Mantener estado único de reportes
 *
 * NO HACE:
 * - Render de gráficas
 * - Control de tabs
 * - Lógica de negocio
 */

// ─────────────────────────────
// IMPORTS OBLIGATORIOS
// (registran listeners de vistas)
// ─────────────────────────────
import './general.js';
import './pasillos.js';
import './personas.js';
import './zonas.js';
import './detalle.js';

import { generarReporte } from '../api.js';
import { iniciarTabsReportes } from '../router.js';

/* ======================================================
   ESTADO ÚNICO (fuente de verdad)
====================================================== */
let resultadoActual = null;
let filtrosActuales = null;
let inicializado = false;

// 🔒 Candado de concurrencia (CRÍTICO)
let cargando = false;

/* ======================================================
   ENTRY POINT
====================================================== */
export function renderReportesScreen(container) {
  console.group('🟢 ReportesScreen init');

  // ─────────────────────────────
  // Estado inicial
  // ─────────────────────────────
  filtrosActuales = filtrosPorDefecto();

  // ⚠️ IMPORTANTE:
  // Este innerHTML se ejecuta UNA SOLA VEZ.
  // El router NUNCA vuelve a tocar esta estructura.
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

      <!-- Paneles (contenedores FIJOS) -->
      <section id="tab-general" class="tab-panel"></section>
      <section id="tab-pasillos" class="tab-panel" style="display:none"></section>
      <section id="tab-personas" class="tab-panel" style="display:none"></section>
      <section id="tab-zonas" class="tab-panel" style="display:none"></section>
      <section id="tab-detalle" class="tab-panel" style="display:none"></section>

    </section>
  `;

  console.log('📦 DOM base de Reportes creado');

  // ─────────────────────────────
  // Inicializaciones (NO tocan tabs)
  // ─────────────────────────────
  initFiltros();
  initEventosGlobales();

  // ─────────────────────────────
  // Router (solo visibilidad + montaje HTML)
  // ─────────────────────────────
  iniciarTabsReportes('general');

  // ─────────────────────────────
  // Fetch inicial (UNA sola vez)
  // ─────────────────────────────
  if (!inicializado) {
    inicializado = true;
    actualizarReportes();
    console.log('📡 Fetch inicial de reportes');
  }

  console.groupEnd();
}


/* ======================================================
   Filtros
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
   Eventos globales (desde vistas)
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
   API (con bloqueo de concurrencia)
====================================================== */
async function actualizarReportes() {
  if (cargando) {
    console.warn('⏸️ Reportes en carga, se ignora llamada duplicada');
    return;
  }

  cargando = true;
  console.log('🟡 Generando reportes', filtrosActuales);

  try {
    resultadoActual = await generarReporte(filtrosActuales);
    if (!resultadoActual) return;

    // 🔔 Evento ÚNICO de datos
    window.dispatchEvent(
      new CustomEvent('reportes:actualizados', {
        detail: resultadoActual
      })
    );

  } catch (err) {
    console.error('❌ Error al generar reportes', err);

  } finally {
    cargando = false;
  }
}

/* ======================================================
   Filtros por defecto
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
   Acceso controlado al estado (solo lectura)
====================================================== */
export function getResultadoActual() {
  return resultadoActual;
}
