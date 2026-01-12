/* ======================================================
   PasillosView Controller
   ======================================================
   - Eje X = rango del filtro (SIEMPRE)
   - Granularidad del eje = agrupar (Día | Semana | Mes)
   - Días/semanas/meses sin datos = 0
   - Logs SOLO para depurar fechas / claves
====================================================== */

import { renderLineChart } from '../charts.js';

/* ======================================================
   CONSTANTES
====================================================== */
const MODOS = ['Individual', 'Comparación', 'Todos separados'];
const PASILLOS_VALIDOS = ['P1', 'P2', 'P3', 'P4'];

const COLORES = ['#2563eb', '#059669', '#d97706', '#dc2626'];
const COLORES_BG = [
  'rgba(37,99,235,.15)',
  'rgba(5,150,105,.15)',
  'rgba(217,119,6,.15)',
  'rgba(220,38,38,.15)'
];

/* ======================================================
   ESTADO
====================================================== */
let dataPorPasillo = {};
let modoActual = MODOS[0];
let pasilloActual = null;
let kpiActual = 'importe';
let ultimoResultado = null;

/* ======================================================
   EVENTOS
====================================================== */
window.addEventListener('reportes:actualizados', e => {
  ultimoResultado = e.detail;
  if (document.getElementById('tab-pasillos')?.classList.contains('active')) {
    renderSeguro();
  }
});

window.addEventListener('reportes:vista-montada', e => {
  if (e.detail?.tab !== 'pasillos') return;
  ultimoResultado ? renderSeguro() : mostrarEstadoEspera();
});

/* ======================================================
   RENDER SEGURO
====================================================== */
function renderSeguro() {
  if (!ultimoResultado) return mostrarEstadoEspera();

  const tab = document.getElementById('tab-pasillos');
  if (!tab) return;

  const controls = tab.querySelector('.pasillos-controls');
  const container = tab.querySelector('#pasillos-container');
  if (!controls || !container) return;

  renderPasillos(ultimoResultado, controls, container);
}

/* ======================================================
   RENDER PRINCIPAL
====================================================== */
function renderPasillos(resultado, controls, container) {
  dataPorPasillo = extraerDatosPasillos(resultado);

  const pasillos = PASILLOS_VALIDOS.filter(p => dataPorPasillo[p]);
  controls.innerHTML = '';
  container.innerHTML = '';

  if (!pasillos.length) {
    container.innerHTML = estadoVacio();
    return;
  }

  if (!pasilloActual || !pasillos.includes(pasilloActual)) {
    pasilloActual = pasillos[0];
  }

  const kpisDisponibles = ['importe', 'piezas', 'devoluciones']
    .filter(k => dataPorPasillo[pasilloActual].series.some(pt => pt[k] != null));

  if (!kpisDisponibles.includes(kpiActual)) {
    kpiActual = kpisDisponibles[0];
  }

  controls.append(
    label('Modo:'),
    select(MODOS, modoActual, v => { modoActual = v; renderActual(container); }),
    label('Pasillo:'),
    select(pasillos, pasilloActual, v => { pasilloActual = v; renderActual(container); }),
    label('KPI:'),
    select(kpisDisponibles, kpiActual, v => { kpiActual = v; renderActual(container); })
  );

  renderActual(container);
}

/* ======================================================
   MODOS
====================================================== */
function renderActual(container) {
  container.innerHTML = '';

  if (modoActual === 'Individual') renderIndividual(container);
  else if (modoActual === 'Comparación') renderComparacion(container);
  else renderTodos(container);
}

/* ======================================================
   CALENDARIO MAESTRO (DESDE FILTRO + AGRUPACIÓN)
====================================================== */
function getAgrupar() {
  // soporta "Dia" / "Día" / "día"
  const a = (ultimoResultado?.rango?.agrupar ?? 'Día');
  const norm = String(a).trim().toLowerCase();
  if (norm === 'mes') return 'Mes';
  if (norm === 'semana') return 'Semana';
  return 'Día';
}

function calendarioDesdeFiltro() {
  const inicio = ultimoResultado?.rango?.inicio;
  const fin = ultimoResultado?.rango?.fin;
  const agrupar = getAgrupar();

  console.log('[PASILLOS] Rango filtro:', inicio, '→', fin, 'Agrupar:', agrupar);

  if (!inicio || !fin) return { labelsKey: [], labelsDate: [], unit: 'day', agrupar };

  if (agrupar === 'Mes') {
    const labelsKey = rangoMensualKey(inicio, fin);         // ['2025-01','2025-02',...]
    const labelsDate = labelsKey.map(k => keyMesToDate(k)); // Date(YYYY,MM,1)
    console.log('[PASILLOS] Labels (Mes):', labelsKey.length, labelsKey.slice(0, 6), '...');
    return { labelsKey, labelsDate, unit: 'month', agrupar };
  }

  if (agrupar === 'Semana') {
    const labelsKey = rangoSemanalKey(inicio, fin);             // ['2025-W01','2025-W02',...]
    const labelsDate = labelsKey.map(k => keySemanaToDate(k));  // Date = lunes de esa semana ISO
    console.log('[PASILLOS] Labels (Semana):', labelsKey.length, labelsKey.slice(0, 6), '...');
    return { labelsKey, labelsDate, unit: 'week', agrupar };
  }

  // Día
  const labelsKey = rangoDiarioKey(inicio, fin);            // ['2025-01-01',...]
  const labelsDate = labelsKey.map(k => keyDiaToDate(k));   // Date(YYYY,MM,DD)
  console.log('[PASILLOS] Labels (Día):', labelsKey.length, labelsKey.slice(0, 6), '...');
  return { labelsKey, labelsDate, unit: 'day', agrupar };
}

/* ======================================================
   GRÁFICAS
====================================================== */
function renderIndividual(container) {
  const bloque = dataPorPasillo[pasilloActual];
  if (!bloque) return;

  const { labelsKey, labelsDate, unit, agrupar } = calendarioDesdeFiltro();
  if (!labelsKey.length) return;

  const data = normalizarSerieContra(labelsKey, bloque.series, kpiActual, agrupar);

  console.log(`[PASILLOS] ${pasilloActual} keys(data) sample:`, labelsKey.slice(0, 6));
  console.log(`[PASILLOS] ${pasilloActual} data sample:`, data.slice(0, 12));

  const canvas = crearCanvas(container);

  renderLineChart(
    canvas,
    labelsDate,
    [{
      label: pasilloActual,
      data,
      borderColor: COLORES[0],
      backgroundColor: COLORES_BG[0],
      spanGaps: true
    }],
    opcionesTime(kpiActual, `Tendencia · ${pasilloActual}`, unit)
  );
}

function renderComparacion(container) {
  const { labelsKey, labelsDate, unit, agrupar } = calendarioDesdeFiltro();
  if (!labelsKey.length) return;

  const canvas = crearCanvas(container);

  const datasets = PASILLOS_VALIDOS
    .filter(p => dataPorPasillo[p])
    .map((p, i) => {
      const data = normalizarSerieContra(labelsKey, dataPorPasillo[p].series, kpiActual, agrupar);
      return {
        label: p,
        data,
        borderColor: COLORES[i],
        backgroundColor: COLORES_BG[i],
        spanGaps: true
      };
    });

  renderLineChart(
    canvas,
    labelsDate,
    datasets,
    opcionesTime(kpiActual, `Comparación · ${kpiActual}`, unit)
  );
}

function renderTodos(container) {
  const { labelsKey, labelsDate, unit, agrupar } = calendarioDesdeFiltro();
  if (!labelsKey.length) return;

  const grid = document.createElement('div');
  grid.className = 'pasillos-grid';

  PASILLOS_VALIDOS.forEach((p, i) => {
    const bloque = dataPorPasillo[p];
    if (!bloque) return;

    const data = normalizarSerieContra(labelsKey, bloque.series, kpiActual, agrupar);

    const localMax = Math.max(...data);
    const suggestedMax = localMax > 0 ? localMax * 1.15 : 1;

    const card = document.createElement('section');
    card.className = 'card';

    const h = document.createElement('h4');
    h.textContent = p;

    const wrapper = document.createElement('div');
    wrapper.style.height = '340px';
    wrapper.style.position = 'relative';

    const canvas = document.createElement('canvas');
    canvas.style.position = 'absolute';
    canvas.style.inset = '0';

    wrapper.appendChild(canvas);
    card.append(h, wrapper);
    grid.appendChild(card);

    renderLineChart(
      canvas,
      labelsDate,
      [{
        label: p,
        data,
        borderColor: COLORES[i],
        backgroundColor: COLORES_BG[i],
        fill: false,
        tension: 0.25,
        spanGaps: true
      }],
      {
        ...opcionesTime(kpiActual, `Tendencia · ${p}`, unit),
        scales: {
          x: { type: 'time', time: { unit } },
          y: { beginAtZero: true, suggestedMax }
        }
      }
    );
  });

  container.appendChild(grid);
}

/* ======================================================
   NORMALIZACIÓN (ALINEA DATOS A LA GRANULARIDAD)
   - labelsKey: claves del eje (día/semana/mes)
   - retorna data[] alineada (faltantes -> 0)
====================================================== */
function normalizarSerieContra(labelsKey, series, kpi, agrupar) {
  const map = new Map();

  for (const p of series || []) {
    const key = normalizarClaveSegunAgrupar(p.fecha ?? p.date ?? p.Fecha, agrupar);
    if (!key) continue;

    const prev = map.get(key) ?? 0;
    const val = Number(p[kpi] ?? 0) || 0;
    map.set(key, prev + val);
  }

  return labelsKey.map(k => map.get(k) ?? 0);
}

function normalizarClaveSegunAgrupar(x, agrupar) {
  if (!x) return null;

  // si ya viene como clave "YYYY-MM-DD"
  if (agrupar === 'Día') {
    if (typeof x === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(x)) return x;
    const d = new Date(x);
    return isNaN(d) ? null : fmtDia(d);
  }

  // Mes: clave "YYYY-MM"
  if (agrupar === 'Mes') {
    if (typeof x === 'string' && /^\d{4}-\d{2}$/.test(x)) return x;
    const d = new Date(x);
    return isNaN(d) ? null : fmtMes(d);
  }

  // Semana: clave "YYYY-Www"
  if (typeof x === 'string' && /^\d{4}-W\d{2}$/.test(x)) return x;
  const d = new Date(x);
  if (isNaN(d)) return null;
  const y = isoWeekYear(d);
  const w = isoWeekNumber(d);
  return `${y}-W${String(w).padStart(2, '0')}`;
}

/* ======================================================
   RANGOS DE CLAVES (Día / Semana / Mes)
====================================================== */
function rangoDiarioKey(inicioISO, finISO) {
  const [yi, mi, di] = inicioISO.split('-').map(Number);
  const [yf, mf, df] = finISO.split('-').map(Number);

  let d = new Date(yi, mi - 1, di);
  const end = new Date(yf, mf - 1, df);

  d.setHours(0, 0, 0, 0);
  end.setHours(0, 0, 0, 0);

  const res = [];
  while (d <= end) {
    res.push(fmtDia(d));
    d.setDate(d.getDate() + 1);
  }
  return res;
}

function rangoMensualKey(inicioISO, finISO) {
  const [yi, mi] = inicioISO.split('-').map(Number);
  const [yf, mf] = finISO.split('-').map(Number);

  let y = yi;
  let m = mi;

  const res = [];
  while (y < yf || (y === yf && m <= mf)) {
    res.push(`${y}-${String(m).padStart(2, '0')}`);
    m++;
    if (m > 12) { m = 1; y++; }
  }
  return res;
}

function rangoSemanalKey(inicioISO, finISO) {
  let d = keyDiaToDate(inicioISO);     // Date local a medianoche
  const end = keyDiaToDate(finISO);

  // mover al lunes ISO
  d = startOfISOMonday(d);

  const res = [];
  while (d <= end) {
    const y = isoWeekYear(d);
    const w = isoWeekNumber(d);
    res.push(`${y}-W${String(w).padStart(2, '0')}`);
    d.setDate(d.getDate() + 7);
  }
  return res;
}

/* ======================================================
   CLAVE -> DATE (para Chart.js time scale)
====================================================== */
function keyDiaToDate(keyDia) {
  const [y, m, d] = keyDia.split('-').map(Number);
  return new Date(y, m - 1, d);
}

function keyMesToDate(keyMes) {
  const [y, m] = keyMes.split('-').map(Number);
  return new Date(y, m - 1, 1);
}

function keySemanaToDate(keySemana) {
  // key: "YYYY-Www" -> lunes de esa semana
  const [yPart, wPart] = keySemana.split('-W');
  const y = Number(yPart);
  const w = Number(wPart);
  return isoWeekToDate(y, w);
}

/* ======================================================
   ISO WEEK HELPERS
====================================================== */
function startOfISOMonday(date) {
  const d = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  d.setHours(0, 0, 0, 0);
  const day = (d.getDay() + 6) % 7; // lunes=0 ... domingo=6
  d.setDate(d.getDate() - day);
  return d;
}

// ISO week-year (puede diferir en primeros/últimos días del año)
function isoWeekYear(date) {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
  return d.getUTCFullYear();
}

function isoWeekNumber(date) {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  const weekNo = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
  return weekNo;
}

function isoWeekToDate(isoYear, isoWeek) {
  // lunes de la semana isoWeek del isoYear
  const simple = new Date(Date.UTC(isoYear, 0, 1 + (isoWeek - 1) * 7));
  const dow = simple.getUTCDay();
  const isoMonday = simple;
  if (dow <= 4) isoMonday.setUTCDate(simple.getUTCDate() - (dow === 0 ? 6 : dow - 1));
  else isoMonday.setUTCDate(simple.getUTCDate() + (8 - dow));
  return new Date(isoMonday.getUTCFullYear(), isoMonday.getUTCMonth(), isoMonday.getUTCDate());
}

/* ======================================================
   FORMATEADORES (sin zona horaria rara)
====================================================== */
function fmtDia(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const da = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${da}`;
}

function fmtMes(d) {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  return `${y}-${m}`;
}

/* ======================================================
   UI HELPERS
====================================================== */
function crearCanvas(container) {
  const c = document.createElement('canvas');
  c.height = 300;
  container.appendChild(c);
  return c;
}

function opcionesTime(kpi, titulo, unit = 'day') {
  return {
    plugins: { title: { display: true, text: titulo } },
    scales: {
      x: { type: 'time', time: { unit } },
      y: { title: { display: true, text: kpi } }
    }
  };
}

function mostrarEstadoEspera() {
  const c = document.getElementById('pasillos-container');
  if (c) c.innerHTML = estadoVacio('Esperando datos…');
}

function estadoVacio(txt = 'No hay datos por pasillo.') {
  return `
    <section class="card empty-state">
      <h4>Reporte por pasillos</h4>
      <p class="text-muted">${txt}</p>
    </section>`;
}

/* ======================================================
   DATOS
====================================================== */
function extraerDatosPasillos(resultado) {
  const datos = {};
  Object.entries(resultado?.por_pasillo || {}).forEach(([k, v]) => {
    const p = normalizarPasillo(k);
    if (p && Array.isArray(v?.series)) datos[p] = { series: v.series };
  });
  return datos;
}

function normalizarPasillo(p) {
  const v = String(p).trim().toUpperCase();
  if (PASILLOS_VALIDOS.includes(v)) return v;
  if (/^[1-4]$/.test(v)) return `P${v}`;
  return null;
}

/* ======================================================
   CONTROLES UI
====================================================== */
function label(t) {
  const l = document.createElement('label');
  l.textContent = t;
  l.style.margin = '0 6px';
  return l;
}

function select(vals, cur, cb) {
  const s = document.createElement('select');
  vals.forEach(v => {
    const o = document.createElement('option');
    o.value = v;
    o.textContent = v;
    s.appendChild(o);
  });
  s.value = cur;
  s.onchange = () => cb(s.value);
  return s;
}
