import { renderLineChart } from '../../../charts.js';
import * as state from '../statePersona.js';
import { estadoVacio } from '../empty.js';

/* ======================================================
   Render Todos separados (una gráfica por persona)
   - KPI dinámico
   - Un punto por fecha
====================================================== */

export function renderizarTodos(container) {
  const personas = state.getPersonasDisponibles();
  const dataPorPersona = state.getDataPorPersona();
  const kpi = state.getKpiActual();

  // Limpieza defensiva
  container.innerHTML = '';

  if (!personas.length) {
    container.innerHTML = estadoVacio('No hay datos para mostrar');
    return;
  }

  const grid = document.createElement('div');
  grid.style.cssText = `
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
    margin-top: 20px;
  `;

  let tieneDatos = false;

  personas.forEach((personaId, index) => {
    const data = dataPorPersona[personaId];

    if (!data || !Array.isArray(data.serie) || !data.serie.length) {
      return;
    }

    // 1️⃣ Normalizar fechas + KPI
    const serieCruda = data.serie
      .map(p => ({
        fecha: convertirPeriodoAFecha(p.periodo, data.periodo),
        valor: Number(p.kpis?.[kpi] ?? 0)
      }))
      .filter(p => p.fecha);

    if (!serieCruda.length) return;

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

    tieneDatos = true;

    // 3️⃣ Card
    const card = document.createElement('div');
    card.style.cssText = `
      background: #fff;
      border-radius: 10px;
      padding: 16px;
      box-shadow: 0 2px 8px rgba(0,0,0,.08);
      border: 1px solid #e2e8f0;
    `;

    const title = document.createElement('h4');
    title.textContent = data.nombre ?? personaId;
    title.style.cssText = `
      margin: 0 0 12px 0;
      font-size: 15px;
      color: #334155;
      font-weight: 600;
    `;

    const canvasWrapper = document.createElement('div');
    canvasWrapper.style.cssText = `
      position: relative;
      width: 100%;
      height: 240px;
    `;

    const canvas = document.createElement('canvas');
    canvasWrapper.appendChild(canvas);

    card.appendChild(title);
    card.appendChild(canvasWrapper);
    grid.appendChild(card);

    // 4️⃣ Render gráfica
    renderLineChart(
      canvas,
      {
        periodo: data.periodo,
        kpi, // 👈 KPI explícito
        series: [
          {
            label: data.nombre ?? personaId,
            color: state.COLORES[index % state.COLORES.length],
            bg: state.COLORES_BG[index % state.COLORES_BG.length],
            kpi,   // 👈 blindaje
            serie
          }
        ]
      },
      {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: { beginAtZero: true }
        }
      }
    );
  });

  if (!tieneDatos) {
    container.innerHTML = estadoVacio('No hay datos válidos para mostrar');
    return;
  }

  container.appendChild(grid);
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
