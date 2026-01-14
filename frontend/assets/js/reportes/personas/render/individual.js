import { renderLineChart } from '../../../charts.js';
import * as state from '../statePersona.js';
import { crearCanvas } from '../ui.js';
import { estadoVacio } from '../empty.js';

/* ======================================================
   Render Individual (Persona seleccionada)
====================================================== */

export function renderizarIndividual(container) {

  const personaId = state.getPersonaActual();
  const data = state.getDataPorPersona()[personaId];
  const resultado = state.getUltimoResultado();

  if (!personaId || !data || !resultado) {
    container.innerHTML = estadoVacio('No hay datos para la persona seleccionada');
    return;
  }

  const kpi = state.getKpiActual();

  /* ======================================================
     1️⃣ CALENDARIO MAESTRO (DÍA / SEMANA / MES / AÑO)
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
     2️⃣ NORMALIZAR SERIE CONTRA CALENDARIO
  ====================================================== */

  const map = new Map();

  for (const p of data.serie || []) {
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

  /* ======================================================
     3️⃣ RENDER
  ====================================================== */

  const canvas = crearCanvas(container);

  renderLineChart(
    canvas,
    {
      periodo: agrupar.toLowerCase(),
      series: [{
        label: data.nombre ?? personaId,
        color: state.COLORES[0],
        bg: state.COLORES_BG[0],
        kpi,
        serie
      }]
    },
    {
      scales: {
        x: {
          type: 'time',
          time: { unit }
        },
        y: {
          beginAtZero: true,
          title: { display: true, text: kpi.toUpperCase() }
        }
      }
    }
  );
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
