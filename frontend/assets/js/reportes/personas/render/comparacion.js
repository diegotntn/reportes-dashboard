import { renderLineChart } from '../../../charts.js';
import * as state from '../statePersona.js';
import { crearCanvas } from '../ui.js';
import { estadoVacio } from '../empty.js';

/* ======================================================
   Render Comparación (Personas)
   - Una serie por persona
   - KPI dinámico
   - Un punto por fecha
====================================================== */

export function renderizarComparacion(container) {
  const personas = state.getPersonasDisponibles();
  const dataPorPersona = state.getDataPorPersona();
  const kpi = state.getKpiActual();

  // Limpieza defensiva
  container.innerHTML = '';

  if (!personas.length) {
    container.innerHTML = estadoVacio('No hay datos para comparar');
    return;
  }

  const series = personas
    .map((personaId, index) => {
      const data = dataPorPersona[personaId];
      if (!data || !Array.isArray(data.serie) || !data.serie.length) {
        return null;
      }

      // 1️⃣ Normalizar fechas + KPI
      const serieCruda = data.serie
        .map(p => ({
          fecha: convertirPeriodoAFecha(p.periodo, data.periodo),
          valor: Number(p.kpis?.[kpi] ?? 0)
        }))
        .filter(p => p.fecha);

      if (!serieCruda.length) return null;

      // 2️⃣ Agrupar y sumar por fecha
      const mapaFechas = {};

      serieCruda.forEach(p => {
        const key = p.fecha.getTime();

        if (!mapaFechas[key]) {
          mapaFechas[key] = {
            fecha: p.fecha,
            total: 0
          };
        }

        mapaFechas[key].total += p.valor;
      });

      const serie = Object.values(mapaFechas).map(p => ({
        fecha: p.fecha,
        kpis: { [kpi]: p.total }
      }));

      return {
        label: data.nombre ?? personaId,
        color: state.COLORES[index % state.COLORES.length],
        bg: state.COLORES_BG[index % state.COLORES_BG.length],
        kpi,   // 👈 explícito (blindaje)
        serie
      };
    })
    .filter(Boolean);

  if (!series.length) {
    container.innerHTML = estadoVacio('No hay datos válidos para comparar');
    return;
  }

  const periodoComun = dataPorPersona[personas[0]]?.periodo || 'mes';
  const canvas = crearCanvas(container);

  renderLineChart(
    canvas,
    {
      periodo: periodoComun,
      kpi,     // 👈 KPI explícito para charts
      series
    },
    {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  );
}

/* ======================================================
   Helpers
====================================================== */

function convertirPeriodoAFecha(key, periodo) {
  if (!key) return null;

  if (periodo === 'mes') {
    const [y, m] = key.split('-').map(Number);
    return new Date(y, m - 1, 1);
  }

  if (periodo === 'dia') {
    const [y, m, d] = key.split('-').map(Number);
    return new Date(y, m - 1, d);
  }

  if (periodo === 'semana') {
    const [y, w] = key.split('-W').map(Number);
    return isoWeekToDate(y, w);
  }

  return null;
}

function isoWeekToDate(y, w) {
  const s = new Date(Date.UTC(y, 0, 1 + (w - 1) * 7));
  const d = s.getUTCDay();
  s.setUTCDate(s.getUTCDate() - (d <= 4 ? d - 1 : d - 8));
  return new Date(s);
}
