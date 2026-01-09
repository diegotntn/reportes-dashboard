/* ======================================================
   GeneralView
   Vista general del dashboard de reportes

   RESPONSABILIDAD
   - Renderizar la vista general
   - Gestionar selección de métrica
   - Ajustar eje X según granularidad
   - Orquestar la gráfica (NO calcula datos)

   ALCANCE
   - UI + interacción visual
   - Consumo exclusivo de charts.js
====================================================== */

import { renderLineChart } from '/assets/js/charts.js';

/* ======================================================
   Estado local (solo UI)
====================================================== */
let currentMetric = null;


/* ======================================================
   Render principal
====================================================== */
export function renderGeneral(resultado) {
  const container = document.getElementById('tab-general');
  const general = resultado?.general;

  /* ───────── DEBUG CONTROLADO ───────── */
  console.log('🟦 GENERAL RECIBIDO');
  console.log('🔢 Puntos:', general?.labels?.length ?? 0);

  /* ───────── Estado vacío ───────── */
  if (
    !general ||
    !Array.isArray(general.labels) ||
    general.labels.length === 0 ||
    !general.series
  ) {
    container.innerHTML = `
      <section class="card">
        <h3>Resumen general</h3>
        <p class="text-muted">No hay datos disponibles.</p>
      </section>
    `;
    return;
  }

  const metricas = Object.keys(general.series);
  if (!metricas.length) {
    container.innerHTML = `
      <section class="card">
        <h3>Resumen general</h3>
        <p class="text-muted">No hay métricas activas.</p>
      </section>
    `;
    return;
  }

  if (!currentMetric || !metricas.includes(currentMetric)) {
    currentMetric = metricas[0];
  }

  /* ───────── UI ───────── */
  container.innerHTML = `
    <section class="general-view">

      <h3>Resumen general</h3>

      <div class="general-controls">
        <label>
          Métrica
          <select id="metric-select">
            ${metricas
              .map(
                m => `
                  <option value="${m}" ${m === currentMetric ? 'selected' : ''}>
                    ${metricLabel(m)}
                  </option>
                `
              )
              .join('')}
          </select>
        </label>
      </div>

      <div class="chart-container">
        <canvas id="general-chart"></canvas>
      </div>

    </section>
  `;

  initGeneralChart(general);
}


/* ======================================================
   Inicialización gráfica
====================================================== */
function initGeneralChart(general) {
  const canvas = document.getElementById('general-chart');
  const metricSelect = document.getElementById('metric-select');

  function draw() {
    renderLineChart(
      canvas,
      general.labels,
      [{
        label: metricLabel(currentMetric),
        data: general.series[currentMetric],
        borderColor: metricColor(currentMetric),
        backgroundColor: metricBgColor(currentMetric),
        fill: true,
        tension: 0.25
      }],
      {
        scales: {
          x: getXAxisOptions(general.labels),
          y: { beginAtZero: true }
        }
      }
    );
  }

  metricSelect.addEventListener('change', e => {
    currentMetric = e.target.value;
    draw();
  });

  draw();
}


/* ======================================================
   Ajuste del eje X (CLAVE DEL COMPORTAMIENTO)
====================================================== */
function getXAxisOptions(labels) {
  const points = labels.length;

  // 🔹 MUCHOS PUNTOS (DÍA)
  if (points > 60) {
    return {
      ticks: {
        autoSkip: true,
        maxTicksLimit: 10,
        callback: () => ''   // 👈 no mostrar fechas
      },
      grid: { display: false }
    };
  }

  // 🔹 SEMANA (aprox por mes)
  if (points > 8 && points <= 60) {
    return {
      ticks: {
        autoSkip: true,
        maxTicksLimit: 6,
        callback: (value, index) => {
          const d = new Date(labels[index]);
          return d.toLocaleString('es-MX', { month: 'long' });
        }
      }
    };
  }

  // 🔹 MES / AÑO
  return {
    ticks: {
      autoSkip: false
    }
  };
}


/* ======================================================
   Utilidades visuales
====================================================== */
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
