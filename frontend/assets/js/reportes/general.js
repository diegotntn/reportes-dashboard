/* ======================================================
   GeneralView Controller
   ======================
   RESPONSABILIDADES:
   - Escuchar actualización de reportes
   - Esperar a que la vista esté montada
   - Poblar selector de métricas
   - Dibujar la gráfica general
   - Reaccionar a cambios de métrica

   CONTRATO:
   resultado.general = {
     periodo: 'dia' | 'semana' | 'mes' | 'anio',
     serie: [ { key, label, kpis, personas } ]
   }
====================================================== */

import { renderLineChart } from '/assets/js/charts.js';

// ─────────────────────────────
// Estado interno persistente
// ─────────────────────────────
let currentMetric = null;
let ultimoResultado = null;
let vistaMontada = false;

// ─────────────────────────────
// Eventos globales
// ─────────────────────────────

// Resultado nuevo desde backend
window.addEventListener('reportes:actualizados', e => {
  ultimoResultado = e.detail;
  intentarRender();
});

// Activación de tab
window.addEventListener('reportes:tab-activada', e => {
  if (e.detail?.tab === 'general') {
    vistaMontada = true;
    intentarRender();
  }
});

// ─────────────────────────────
// Render seguro (no se pierde)
// ─────────────────────────────
function intentarRender() {
  if (!ultimoResultado) return;
  if (!vistaMontada) return;

  const container = document.getElementById('tab-general');
  const select = document.getElementById('metric-select');
  const canvas = document.getElementById('general-chart');

  if (!container || !select || !canvas) {
    console.warn('[GeneralView] DOM aún no disponible');
    return;
  }

  renderGeneral(ultimoResultado);
}

// ─────────────────────────────
// Render principal
// ─────────────────────────────
function renderGeneral(resultado) {

  const general = resultado?.general;

  // Validación NUEVA (contrato actual)
  if (!general || !Array.isArray(general.serie) || general.serie.length === 0) {
    mostrarEstadoVacio();
    return;
  }

  // Métricas disponibles desde el primer punto
  const metricas = Object.keys(general.serie[0]?.kpis || {});
  if (!metricas.length) {
    mostrarEstadoVacio();
    return;
  }

  // Métrica por defecto
  if (!currentMetric || !metricas.includes(currentMetric)) {
    currentMetric = metricas[0];
  }

  const select = document.getElementById('metric-select');
  const canvas = document.getElementById('general-chart');

  // ───────── Poblar selector
  select.innerHTML = metricas.map(m => `
    <option value="${m}" ${m === currentMetric ? 'selected' : ''}>
      ${metricLabel(m)}
    </option>
  `).join('');

  const draw = () => {
    // Serie filtrada por métrica (SIN perder personas)
    const serieFiltrada = general.serie.map(p => ({
      ...p,
      fecha: convertirKeyAFecha(p.key, general.periodo), // 🔑 CLAVE
      kpis: {
        importe: Number(p.kpis[currentMetric] ?? 0)
      }
    }));

    console.table(
  serieFiltrada.map(p => ({
    key: p.key,
    fecha: p.fecha,
    periodo: general.periodo
  }))
);
    // Llamada CORREGIDA a la nueva API de charts.js
    renderLineChart(
      canvas,
      {
        periodo: general.periodo,
        series: [  // ¡Ahora es 'series' (array)!
          { 
            label: metricLabel(currentMetric),
            color: '#2563eb',
            bg: 'rgba(37,99,235,.15)',
            serie: serieFiltrada
          }
        ]
      },
      {
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: v => Number(v).toLocaleString('es-MX')
            },
            title: {
              display: true,
              text: metricLabel(currentMetric)
            }
          },
          x: {
            type: 'time',
            time: {
              unit: 
                general.periodo === 'dia' ? 'day' :
                general.periodo === 'semana' ? 'week' :
                general.periodo === 'mes' ? 'month' :
                'year'
            }
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
      <p class="text-muted">
        No hay datos disponibles para el rango seleccionado.
      </p>
    </section>
  `;
}

// ─────────────────────────────
// Utilidades visuales
// ─────────────────────────────
function metricLabel(m) {
  if (m === 'importe') return 'Importe';
  if (m === 'devoluciones') return 'Devoluciones';
  if (m === 'piezas') return 'Piezas';
  return m;
}

function convertirKeyAFecha(key, periodo) {
  if (!key) return null;

  // dia: YYYY-MM-DD
  if (periodo === 'dia') {
    const [y, m, d] = key.split('-').map(Number);
    return new Date(y, m - 1, d);
  }

  // semana: YYYY-MM-DD (inicio de semana)
  if (periodo === 'semana') {
    const [y, m, d] = key.split('-').map(Number);
    return new Date(y, m - 1, d);
  }

  // mes: YYYY-MM
  if (periodo === 'mes') {
    const [y, m] = key.split('-').map(Number);
    return new Date(y, m - 1, 1);
  }

  // anio: YYYY
  if (periodo === 'anio') {
    const y = Number(key);
    return new Date(y, 0, 1);
  }

  return null;
}


// helper ISO (idéntico al que ya usas)
function isoWeekToDate(y, w) {
  const s = new Date(Date.UTC(y, 0, 1 + (w - 1) * 7));
  const d = s.getUTCDay();
  s.setUTCDate(s.getUTCDate() - (d <= 4 ? d - 1 : d - 8));
  return new Date(s);
}
