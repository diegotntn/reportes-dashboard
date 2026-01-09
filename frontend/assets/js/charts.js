/* ======================================================
   charts.js
   Motor gráfico genérico para dashboards
====================================================== */

/* ======================================================
   Configuración base compartida
====================================================== */
const BASE_OPTIONS = {
  responsive: true,
  maintainAspectRatio: false,

  interaction: {
    mode: 'index',
    intersect: false
  },

  plugins: {
    legend: {
      display: true,
      position: 'bottom',
      labels: {
        usePointStyle: true,
        boxWidth: 8,
        color: '#374151'
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
      callbacks: {
        label(ctx) {
          const value = ctx.parsed?.y ?? ctx.parsed;
          return ` ${ctx.dataset.label}: ${value.toLocaleString()}`;
        }
      }
    }
  },

  scales: {
    x: {
      grid: { display: false },
      ticks: {
        color: '#6b7280',
        autoSkip: true
      }
    },
    y: {
      beginAtZero: true,
      grid: { color: '#e5e7eb' },
      ticks: { color: '#6b7280' }
    }
  }
};


/* ======================================================
   Utilidades internas
====================================================== */

/**
 * Destruye la gráfica existente asociada al canvas.
 */
function destroyIfExists(canvas) {
  const chart = Chart.getChart(canvas);
  if (chart) {
    chart.destroy();
  }
}

/**
 * Ajusta ticks y puntos según densidad de datos
 */
function adaptScaleOptions(labelsCount) {
  if (labelsCount > 180) {
    return { maxTicksLimit: 12, pointRadius: 1 };
  }
  if (labelsCount > 60) {
    return { maxTicksLimit: 10, pointRadius: 2 };
  }
  if (labelsCount > 20) {
    return { maxTicksLimit: 12, pointRadius: 3 };
  }
  return { maxTicksLimit: labelsCount, pointRadius: 5 };
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
      ...options
    }
  });
}


/* ======================================================
   GRÁFICA DE LÍNEA
====================================================== */
export function renderLineChart(canvas, labels, datasets, options = {}) {
  destroyIfExists(canvas);

  const { maxTicksLimit, pointRadius } = adaptScaleOptions(labels.length);

  return new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: datasets.map(ds => ({
        tension: 0.35,
        fill: true,
        spanGaps: true,
        pointRadius,
        pointHoverRadius: pointRadius + 2,
        ...ds
      }))
    },
    options: {
      ...BASE_OPTIONS,
      scales: {
        ...BASE_OPTIONS.scales,
        x: {
          ...BASE_OPTIONS.scales.x,
          ticks: {
            ...BASE_OPTIONS.scales.x.ticks,
            maxTicksLimit
          }
        }
      },
      ...options
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
   RESET DE ZOOM (si usas plugin zoom)
====================================================== */
export function resetZoom(canvas) {
  const chart = Chart.getChart(canvas);
  if (chart && typeof chart.resetZoom === 'function') {
    chart.resetZoom();
  }
}
