/* ======================================================
   charts.js
   Motor gráfico genérico para dashboards
   Chart.js 4.x
====================================================== */

/* ======================================================
   CONFIGURACIÓN BASE
====================================================== */

const BASE_OPTIONS = {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 2.5,

  interaction: {
    mode: 'index',
    intersect: false
  },

  animation: { duration: 300 },

  plugins: {
    legend: {
      display: true,
      position: 'bottom',
      labels: {
        usePointStyle: true,
        boxWidth: 8,
        padding: 16,
        color: '#374151',
        font: { size: 12, weight: '500' }
      }
    },

    tooltip: {
      enabled: true,
      backgroundColor: '#111827',
      titleColor: '#ffffff',
      bodyColor: '#ffffff',
      padding: 10,
      borderWidth: 1,
      borderColor: '#374151',
      displayColors: false,

      callbacks: {
        title(items) {
          const p = items?.[0]?.raw;
          return p?.label ?? '';
        },

        label(ctx) {
          const p = ctx.raw;
          if (!p?.kpis) return '';

          // 🔑 Resolver KPI igual que el dataset
          const kpi =
            ctx.dataset?.kpi ??
            ctx.chart?.config?._config?.kpi ??
            'importe';

          const valor =
            p.kpis?.[kpi] ??
            p.kpis?.importe ??
            0;

          return `Total: ${Number(valor).toLocaleString('es-MX')}`;
        }

      }
    }
  },

  scales: {
    y: {
      beginAtZero: true,
      grid: { color: '#e5e7eb', drawBorder: false },
      ticks: { color: '#6b7280', maxTicksLimit: 6 }
    },

    x: {
      grid: { display: false },
      ticks: { color: '#6b7280', autoSkip: true }
    }
  }
};

/* ======================================================
   HELPERS
====================================================== */

function destroyIfExists(canvas) {
  const chart = Chart.getChart(canvas);
  if (chart) chart.destroy();
}

function adaptDensity(count) {
  if (count > 180) return { maxTicksLimit: 8, pointRadius: 0 };
  if (count > 60)  return { maxTicksLimit: 10, pointRadius: 2 };
  if (count > 20)  return { maxTicksLimit: 12, pointRadius: 3 };
  return { maxTicksLimit: count, pointRadius: 4 };
}

/* ======================================================
   KPI RESOLVER (CLAVE DE TODO)
   - NO rompe nada
   - Default: 'importe'
====================================================== */

function resolveKpi(p, cfg, payload) {
  const kpi =
    cfg?.kpi ??
    payload?.kpi ??
    'importe';

  return Number(
    p?.kpis?.[kpi] ??
    p?.kpis?.importe ??
    0
  );
}

/* ======================================================
   DATASET BUILDER (RETROCOMPATIBLE)
====================================================== */

function buildDataset(serie, cfg, density, payload) {
  return {
    label: cfg.label,
    borderColor: cfg.color,
    backgroundColor: cfg.bg,
    tension: 0.3,
    fill: cfg.fill ?? true,
    spanGaps: true,
    pointRadius: density.pointRadius,
    pointHoverRadius: density.pointRadius + 2,

    data: serie.map(p => ({
      x: p.fecha,
      y: resolveKpi(p, cfg, payload),
      ...p
    }))
  };
}

/* ======================================================
   LINE CHART — UNA O VARIAS SERIES
====================================================== */

export function renderLineChart(canvas, payload, options = {}) {

  destroyIfExists(canvas);

  if (!payload?.series || payload.series.length === 0) return;

  const allPoints = payload.series.reduce(
    (a, s) => a + (s.serie?.length || 0),
    0
  );

  const density = adaptDensity(allPoints);

  const datasets = payload.series.map(s =>
    buildDataset(s.serie, s, density, payload)
  );

  return new Chart(canvas, {
    type: 'line',

    data: { datasets },

    options: {
      ...BASE_OPTIONS,
      ...options,

      plugins: {
        ...BASE_OPTIONS.plugins,
        ...(options.plugins || {})
      },

      scales: {
        y: {
          ...BASE_OPTIONS.scales.y,
          ...(options.scales?.y || {})
        },

        x: {
          type: 'time',
          time: {
            unit:
              payload.periodo === 'dia' ? 'day' :
              payload.periodo === 'semana' ? 'week' :
              payload.periodo === 'mes' ? 'month' :
              'year'
          },
          ticks: {
            ...BASE_OPTIONS.scales.x.ticks,
            maxTicksLimit: density.maxTicksLimit,
            ...(options.scales?.x?.ticks || {})
          },
          ...(options.scales?.x || {})
        }
      }
    }
  });
}

/* ======================================================
   BAR CHART (SIN CAMBIOS)
====================================================== */

export function renderBarChart(canvas, general, options = {}) {

  destroyIfExists(canvas);
  if (!general?.serie) return;

  return new Chart(canvas, {
    type: 'bar',
    data: {
      labels: general.serie.map(p => p.label),
      datasets: [{
        label: 'Importe',
        data: general.serie.map(p => p.kpis.importe),
        borderRadius: 6,
        maxBarThickness: 48,
        backgroundColor: '#2563eb'
      }]
    },
    options: { ...BASE_OPTIONS, ...options }
  });
}

/* ======================================================
   DONUT / PIE (SIN CAMBIOS)
====================================================== */

export function renderDonutChart(canvas, labels, data, options = {}) {

  destroyIfExists(canvas);

  return new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        borderWidth: 1,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'right' },
        tooltip: BASE_OPTIONS.plugins.tooltip
      },
      ...options
    }
  });
}

/* ======================================================
   RESET ZOOM
====================================================== */

export function resetZoom(canvas) {
  const chart = Chart.getChart(canvas);
  if (chart?.resetZoom) chart.resetZoom();
}
