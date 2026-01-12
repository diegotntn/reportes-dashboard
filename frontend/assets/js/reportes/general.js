/* ======================================================
   GeneralView Controller
   ======================
   RESPONSABILIDADES:
   - Escuchar actualización de reportes
   - Esperar a que la vista esté montada
   - Poblar controles de la vista
   - Dibujar la gráfica
   - Responder a cambios de métrica

   NO HACE:
   - Cargar vistas HTML
   - Navegación de tabs
====================================================== */

import { renderLineChart } from '/assets/js/charts.js';

// ─────────────────────────────
// Estado interno
// ─────────────────────────────
let currentMetric = null;
let ultimoResultado = null;

// ─────────────────────────────
// Eventos globales
// ─────────────────────────────

// Datos actualizados desde backend
window.addEventListener('reportes:actualizados', e => {
  ultimoResultado = e.detail;
  intentarRender();
});

// Cambio de tab
window.addEventListener('reportes:tab-activada', e => {
  if (e.detail.tab === 'general') {
    intentarRender();
  }
});

// ─────────────────────────────
// Intento seguro de render
// ─────────────────────────────
function intentarRender() {
  if (!ultimoResultado) return;

  const container = document.getElementById('tab-general');
  const select = document.getElementById('metric-select');
  const canvas = document.getElementById('general-chart');

  // Vista aún no montada
  if (!container || !select || !canvas) {
    console.warn('[GeneralView] Vista no montada todavía');
    return;
  }

  renderGeneral(ultimoResultado);
}

// ─────────────────────────────
// Render principal
// ─────────────────────────────
function renderGeneral(resultado) {
  const general = resultado?.general;
  const agrupacion = resultado?.agrupar || resultado?.resumen?.agrupar;

  if (!general?.labels?.length || !general?.series) {
    mostrarEstadoVacio();
    return;
  }

  const metricas = Object.keys(general.series);
  if (!metricas.length) {
    mostrarEstadoVacio();
    return;
  }

  if (!currentMetric || !metricas.includes(currentMetric)) {
    currentMetric = metricas[0];
  }

  const select = document.getElementById('metric-select');
  const canvas = document.getElementById('general-chart');

  // Poblar selector
  select.innerHTML = metricas.map(m => `
    <option value="${m}" ${m === currentMetric ? 'selected' : ''}>
      ${metricLabel(m)}
    </option>
  `).join('');

  const draw = () => {
    const labels = normalizeLabels(general.labels, agrupacion);
    const values = general.series[currentMetric].map(v => Number(v) || 0);

    renderLineChart(
      canvas,
      labels,
      [{
        label: metricLabel(currentMetric),
        data: values,
        fill: true,
        tension: 0.25,
        borderColor: metricColor(currentMetric),
        backgroundColor: metricBgColor(currentMetric)
      }],
      {
        scales: {
          x: buildXAxis(agrupacion),
          y: {
            beginAtZero: true,
            ticks: {
              callback: v => v.toLocaleString('es-MX')
            }
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        }
      }
    );
  };

  select.onchange = e => {
    currentMetric = e.target.value;
    draw();
  };

  draw();
}

// ─────────────────────────────
// Estado vacío
// ─────────────────────────────
function mostrarEstadoVacio() {
  const container = document.getElementById('tab-general');
  if (!container) return;

  container.innerHTML = `
    <section class="card">
      <h3>Resumen general</h3>
      <p class="text-muted">No hay datos disponibles.</p>
    </section>
  `;
}

// ─────────────────────────────
// Normalización de labels (ISO)
// ─────────────────────────────
function normalizeLabels(labels, agrupacion) {

  if (agrupacion === 'Mes') {
    return labels
      .map(l => /^\d{4}-\d{2}$/.test(l) ? `${l}-01` : l)
      .filter(l => /^\d{4}-\d{2}-\d{2}$/.test(l));
  }

  if (agrupacion === 'Dia' || agrupacion === 'Semana') {
    return labels;
  }

  if (agrupacion === 'Año') {
    return labels.map(y => `${y}-01-01`);
  }

  return labels;
}

// ─────────────────────────────
// Configuración eje X
// ─────────────────────────────
function buildXAxis(agrupacion) {

  const base = {
    type: 'time',
    ticks: { source: 'data' }
  };

  if (agrupacion === 'Mes') {
    base.time = { unit: 'month', displayFormats: { month: 'MMM yyyy' } };
  } else if (agrupacion === 'Semana') {
    base.time = { unit: 'week', displayFormats: { week: "'Sem' w" } };
  } else if (agrupacion === 'Dia') {
    base.time = { unit: 'day', displayFormats: { day: 'dd MMM' } };
  } else {
    base.time = { unit: 'year', displayFormats: { year: 'yyyy' } };
  }

  return base;
}

// ─────────────────────────────
// Utilidades visuales
// ─────────────────────────────
function metricLabel(m) {
  if (m === 'importe') return 'Importe';
  if (m === 'devoluciones') return 'Devoluciones';
  return 'Piezas';
}

function metricColor(m) {
  if (m === 'importe') return '#2563eb';
  if (m === 'devoluciones') return '#dc2626';
  return '#16a34a';
}

function metricBgColor(m) {
  if (m === 'importe') return 'rgba(37,99,235,.15)';
  if (m === 'devoluciones') return 'rgba(220,38,38,.15)';
  return 'rgba(22,163,74,.15)';
}
