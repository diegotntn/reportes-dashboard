/* ======================================================
   charts.js
   Motor gráfico genérico para dashboards
   Compatible con Chart.js 4 + eje time
====================================================== */

/* ======================================================
   Configuración base para Chart.js
   - Segura para grids (Todos separados)
   - Compatible con eje time
   - Estable en resize / zoom
====================================================== */

const BASE_OPTIONS = {
  responsive: true,

  // 🔒 CLAVE: mantener proporción para evitar loops de resize
  maintainAspectRatio: true,
  aspectRatio: 2.5,

  interaction: {
    mode: 'index',
    intersect: false
  },

  animation: {
    duration: 300
  },

  plugins: {
    legend: {
      display: true,
      position: 'bottom',
      labels: {
        usePointStyle: true,
        boxWidth: 8,
        padding: 16,
        color: '#374151',
        font: {
          size: 12,
          weight: '500'
        }
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
        label(ctx) {
          const v = ctx.parsed?.y ?? ctx.parsed;
          return `${ctx.dataset.label}: ${Number(v).toLocaleString('es-MX')}`;
        }
      }
    }
  },

  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: '#e5e7eb',
        drawBorder: false
      },
      ticks: {
        color: '#6b7280',
        maxTicksLimit: 6
      }
    },

    x: {
      grid: {
        display: false
      },
      ticks: {
        color: '#6b7280',
        maxRotation: 0,
        autoSkip: true
      }
    }
  }
};


/* ======================================================
   Utilidades internas
====================================================== */

/**
 * Destruye la gráfica existente asociada al canvas
 */
function destroyIfExists(canvas) {
  const chart = Chart.getChart(canvas);
  if (chart) chart.destroy();
}

/**
 * Ajuste automático de densidad visual
 */
function adaptDensity(count) {
  if (count > 180) return { maxTicksLimit: 8, pointRadius: 0 };
  if (count > 60)  return { maxTicksLimit: 10, pointRadius: 2 };
  if (count > 20)  return { maxTicksLimit: 12, pointRadius: 3 };
  return { maxTicksLimit: count, pointRadius: 4 };
}

/* ======================================================
   GRÁFICA DE LÍNEA
   - Soporta eje categórico y eje time
   - Convierte labels → {x,y} SOLO si es time
====================================================== */
export function renderLineChart(canvas, labels, datasets, options = {}) {
  console.log('📐 Chart container size', {
      canvas: canvas,
      parent: canvas.parentElement?.getBoundingClientRect()
    });

  destroyIfExists(canvas);

  const isTimeScale = options.scales?.x?.type === 'time';

  const totalPoints =
    datasets?.[0]?.data?.length ??
    labels?.length ??
    0;

  const { maxTicksLimit, pointRadius } = adaptDensity(totalPoints);

  // 🔁 Normalización de datasets para eje time
  const preparedDatasets = datasets.map(ds => {
    if (!isTimeScale) return ds;

    return {
      ...ds,
      data: labels.map((label, i) => ({
        x: label,
        y: ds.data[i]
      }))
    };
  });

  return new Chart(canvas, {
    type: 'line',

    data: {
      // ⚠️ labels NO se usan en eje time
      labels: isTimeScale ? undefined : labels,
      datasets: preparedDatasets.map(ds => ({
        tension: 0.3,
        fill: true,
        spanGaps: true,
        pointRadius,
        pointHoverRadius: pointRadius + 2,
        ...ds
      }))
    },

    options: {
      ...BASE_OPTIONS,
      ...options,

      scales: {
        /* ───────── EJE Y ───────── */
        y: {
          beginAtZero: true,
          grid: { color: '#e5e7eb' },
          ticks: { color: '#6b7280' },
          ...(options.scales?.y || {})
        },

        /* ───────── EJE X ───────── */
        x: {
          grid: { display: false },
          ticks: {
            color: '#6b7280',
            maxTicksLimit,
            ...(options.scales?.x?.ticks || {})
          },
          ...(options.scales?.x || {})
        }
      }
    }
  });
}

/* ======================================================
   GRÁFICA DE BARRAS
====================================================== */
export function renderBarChart(canvas, labels, datasets, options = {}) {

  destroyIfExists(canvas);

  return new Chart(canvas, {
    type: 'bar',

    data: {
      labels,
      datasets: datasets.map(ds => ({
        borderRadius: 6,
        maxBarThickness: 48,
        ...ds
      }))
    },

    options: {
      ...BASE_OPTIONS,
      ...options,
      scales: {
        ...(options.scales || {})
      }
    }
  });
}

/* ======================================================
   GRÁFICA DONUT / PIE
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
   RESET DE ZOOM
====================================================== */
export function resetZoom(canvas) {
  const chart = Chart.getChart(canvas);
  if (chart?.resetZoom) chart.resetZoom();
}
