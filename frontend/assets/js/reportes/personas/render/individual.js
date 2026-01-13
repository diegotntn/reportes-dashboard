import { renderLineChart } from '../../../charts.js';
import * as state from '../statePersona.js';
import { crearCanvas } from '../ui.js';
import { estadoVacio } from '../empty.js';

/* ======================================================
   Render Individual (Persona seleccionada)
====================================================== */

export function renderizarIndividual(container) {
  const personaId = state.getPersonaActual();
  const mapaPersonas = state.getDataPorPersona();
  const data = mapaPersonas[personaId];

  if (!personaId || !data) {
    container.innerHTML = estadoVacio('No hay datos para la persona seleccionada');
    return;
  }

  const kpi = state.getKpiActual();

  /* ───────── 1. Normalizar fechas + KPI ───────── */
  const serieCruda = data.serie
    .map(p => ({
      fecha: convertirPeriodoAFecha(p.periodo, data.periodo),
      valor: Number(p.kpis?.[kpi] ?? 0)
    }))
    .filter(p => p.fecha);

  if (!serieCruda.length) {
    container.innerHTML = estadoVacio('No hay datos para el periodo');
    return;
  }

  /* ───────── 2. Agrupar y sumar por fecha ───────── */
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

  /* ───────── 3. Render gráfica ───────── */
  const canvas = crearCanvas(container);

  renderLineChart(canvas, {
    periodo: data.periodo,
    kpi, // 👈 KPI explícito (retrocompatible)
    series: [
      {
        label: data.nombre ?? personaId,
        color: state.COLORES[0],
        bg: state.COLORES_BG[0],
        kpi,   // 👈 redundante a propósito (blindaje)
        serie
      }
    ]
  });
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
