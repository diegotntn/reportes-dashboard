import { renderLineChart } from '../../../charts.js';
import * as state from '../statePersona.js';
import { estadoVacio } from '../empty.js';

/* ======================================================
   Render Todos separados (una gráfica por persona)
====================================================== */

export function renderizarTodos(container) {

  const personas = state.getPersonasDisponibles();
  const dataPorPersona = state.getDataPorPersona();
  const resultado = state.getUltimoResultado();
  const kpi = state.getKpiActual();

  container.innerHTML = '';

  if (!personas.length || !resultado) {
    container.innerHTML = estadoVacio('No hay datos para mostrar');
    return;
  }

  /* ======================================================
     1️⃣ CALENDARIO MAESTRO
  ====================================================== */

  const inicio = resultado?.rango?.inicio;
  const fin = resultado?.rango?.fin;
  const agruparRaw = String(resultado?.rango?.agrupar ?? 'Dia').toLowerCase();

  const agrupar =
    agruparRaw.startsWith('anio') ? 'Anio' :
    agruparRaw.startsWith('mes')  ? 'Mes'  :
    agruparRaw.startsWith('sem')  ? 'Semana' :
    'Dia';

  if (!inicio || !fin) {
    container.innerHTML = estadoVacio('Rango inválido');
    return;
  }

  let labelsKey = [];
  let labelsDate = [];
  let unit = 'day';

  if (agrupar === 'Anio') {
    labelsKey = rangoAnualKey(inicio, fin);
    labelsDate = labelsKey.map(keyAnioToDate);
    unit = 'year';

  } else if (agrupar === 'Mes') {
    labelsKey = rangoMensualKey(inicio, fin);
    labelsDate = labelsKey.map(keyMesToDate);
    unit = 'month';

  } else if (agrupar === 'Semana') {
    labelsKey = rangoSemanalKey(inicio, fin);
    labelsDate = labelsKey.map(keySemanaToDate);
    unit = 'week';

  } else {
    labelsKey = rangoDiarioKey(inicio, fin);
    labelsDate = labelsKey.map(keyDiaToDate);
    unit = 'day';
  }

  if (!labelsKey.length) {
    container.innerHTML = estadoVacio('Sin calendario');
    return;
  }

  /* ======================================================
     2️⃣ GRID
  ====================================================== */

  const grid = document.createElement('div');
  grid.style.cssText = `
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
    margin-top: 20px;
  `;

  let tieneDatos = false;

  /* ======================================================
     3️⃣ UNA GRÁFICA POR PERSONA
  ====================================================== */

  personas.forEach((personaId, index) => {
    const data = dataPorPersona[personaId];
    if (!data || !Array.isArray(data.serie)) return;

    const map = new Map();

    for (const p of data.serie) {
      const key = normalizarClave(p.periodo, agrupar);
      if (!key) continue;

      const val = Number(p.kpis?.[kpi]);
      map.set(key, (map.get(key) ?? 0) + (Number.isFinite(val) ? val : 0));
    }

    const serie = labelsKey.map((key, i) => ({
      key,
      fecha: labelsDate[i],
      kpis: {
        [kpi]: map.get(key) ?? 0
      }
    }));

    if (!serie.some(p => p.kpis[kpi] !== 0)) return;

    tieneDatos = true;

    /* ───────── Card ───────── */
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

    card.append(title, canvasWrapper);
    grid.appendChild(card);

    /* ───────── Render ───────── */
    renderLineChart(
      canvas,
      {
        periodo: agrupar.toLowerCase(),
        series: [{
          label: data.nombre ?? personaId,
          color: state.COLORES[index % state.COLORES.length],
          bg: state.COLORES_BG[index % state.COLORES_BG.length],
          kpi,
          serie
        }]
      },
      {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            type: 'time',
            time: { unit }
          },
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: kpi.toUpperCase()
            }
          }
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
   HELPERS — CALENDARIO MAESTRO
====================================================== */

function normalizarClave(key, agrupar) {
  if (!key) return null;

  if (agrupar === 'Dia') return key.slice(0, 10);
  if (agrupar === 'Mes') return key.slice(0, 7);
  if (agrupar === 'Anio') return key.slice(0, 4);

  const d = keyDiaToDate(key);
  return `${isoWeekYear(d)}-W${String(isoWeekNumber(d)).padStart(2, '0')}`;
}

/* ======================================================
   RANGOS
====================================================== */

function rangoDiarioKey(i, f) {
  let d = keyDiaToDate(i), end = keyDiaToDate(f), res = [];
  while (d <= end) { res.push(fmtDia(d)); d.setDate(d.getDate() + 1); }
  return res;
}

function rangoMensualKey(i, f) {
  const [yi, mi] = i.split('-').map(Number);
  const [yf, mf] = f.split('-').map(Number);
  let y = yi, m = mi, res = [];
  while (y < yf || (y === yf && m <= mf)) {
    res.push(`${y}-${String(m).padStart(2, '0')}`);
    if (++m > 12) { m = 1; y++; }
  }
  return res;
}

function rangoSemanalKey(i, f) {
  let d = startOfISOMonday(keyDiaToDate(i)), end = keyDiaToDate(f), res = [];
  while (d <= end) {
    res.push(`${isoWeekYear(d)}-W${String(isoWeekNumber(d)).padStart(2, '0')}`);
    d.setDate(d.getDate() + 7);
  }
  return res;
}

function rangoAnualKey(i, f) {
  const yi = Number(i.slice(0, 4));
  const yf = Number(f.slice(0, 4));
  const res = [];
  for (let y = yi; y <= yf; y++) res.push(String(y));
  return res;
}

/* ======================================================
   KEY → DATE
====================================================== */

function keyDiaToDate(k) {
  const [y, m, d] = k.split('-').map(Number);
  return new Date(y, m - 1, d);
}

function keyMesToDate(k) {
  const [y, m] = k.split('-').map(Number);
  return new Date(y, m - 1, 1);
}

function keySemanaToDate(k) {
  const [y, w] = k.split('-W').map(Number);
  return isoWeekToDate(y, w);
}

function keyAnioToDate(k) {
  return new Date(Number(k), 0, 1);
}

/* ======================================================
   ISO WEEK HELPERS
====================================================== */

function startOfISOMonday(d) {
  const r = new Date(d);
  r.setDate(r.getDate() - ((r.getDay() + 6) % 7));
  return r;
}

function isoWeekYear(d) {
  const t = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  t.setUTCDate(t.getUTCDate() + 4 - (t.getUTCDay() || 7));
  return t.getUTCFullYear();
}

function isoWeekNumber(d) {
  const t = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  t.setUTCDate(t.getUTCDate() + 4 - (t.getUTCDay() || 7));
  return Math.ceil((((t - new Date(Date.UTC(t.getUTCFullYear(), 0, 1))) / 86400000) + 1) / 7);
}

function isoWeekToDate(y, w) {
  const s = new Date(Date.UTC(y, 0, 1 + (w - 1) * 7));
  const d = s.getUTCDay();
  s.setUTCDate(s.getUTCDate() - (d <= 4 ? d - 1 : d - 8));
  return new Date(s);
}

function fmtDia(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}
