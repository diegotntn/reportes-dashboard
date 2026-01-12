/* ======================================================
   PasillosView Controller
   =======================
   - Usa Chart.js vía charts.js (mismo look & feel que General)
   - Eje diario completo (días sin datos = 0)
   - Escala Y compartida en "Todos separados"
   - FIX: evita “crecer infinitamente” en Todos separados
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
   ESTADO LOCAL
====================================================== */
let dataPorPasillo = {};
let modoActual = MODOS[0];
let pasilloActual = null;
let kpiActual = 'importe';
let ultimoResultado = null;

/* ======================================================
   EVENTOS GLOBALES
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

  // Controles UI
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
   GRÁFICAS (Chart.js)
====================================================== */
function renderIndividual(container) {
  const bloque = dataPorPasillo[pasilloActual];
  if (!bloque) return;

  // Calendario diario completo SOLO del rango del pasillo
  const labelsISO = generarRangoFechasISO(bloque.series);
  const { labelsDate, data } = normalizarSerieContra(labelsISO, bloque.series, kpiActual);

  const canvas = crearCanvas(container);

  renderLineChart(
    canvas,
    labelsDate,
    [{
      label: pasilloActual,
      data,
      borderColor: COLORES[0],
      backgroundColor: COLORES_BG[0],
      // importante para "días sin datos = 0": no hace falta spanGaps, siempre hay valor
      spanGaps: true
    }],
    opcionesTime(kpiActual, `Tendencia · ${pasilloActual}`)
  );
}

function renderComparacion(container) {
  // Base = calendario global (unificado) para que comparen igual
  const labelsISO = generarRangoFechasISO_GLOBAL(dataPorPasillo);
  const labelsDate = labelsISO.map(iso => new Date(iso));

  const canvas = crearCanvas(container);

  const datasets = PASILLOS_VALIDOS
    .filter(p => dataPorPasillo[p])
    .map((p, i) => {
      const { data } = normalizarSerieContra(labelsISO, dataPorPasillo[p].series, kpiActual);
      return {
        label: p,
        data,
        borderColor: COLORES[i],
        backgroundColor: COLORES_BG[i],
        spanGaps: true
      };
    });

  if (!datasets.length) return;

  renderLineChart(
    canvas,
    labelsDate,
    datasets,
    opcionesTime(kpiActual, `Comparación · ${kpiActual.toUpperCase()}`)
  );
}

function renderTodos(container) {
  const grid = document.createElement('div');
  grid.className = 'pasillos-grid';

  /* ======================================================
     1) Construir eje maestro ISO (YYYY-MM-DD)
  ====================================================== */
  const allDates = new Set();

  PASILLOS_VALIDOS.forEach(p => {
    const bloque = dataPorPasillo[p];
    if (!bloque) return;

    for (const pt of (bloque.series || [])) {
      const iso = toISODate(pt.fecha ?? pt.date ?? pt.Fecha);
      if (iso) allDates.add(iso);
    }
  });

  const labelsISO = [...allDates].sort();

  if (!labelsISO.length) {
    container.innerHTML = estadoVacio('No hay fechas válidas.');
    return;
  }

  /* ======================================================
     2) Render por pasillo (escala Y LOCAL)
  ====================================================== */
  PASILLOS_VALIDOS.forEach((p, i) => {
    const bloque = dataPorPasillo[p];
    if (!bloque) return;

    // Normalizar contra el MISMO eje X
    const { labelsDate, data } =
      normalizarSerieContra(labelsISO, bloque.series, kpiActual);

    // 🔑 ESCALA LOCAL POR PASILLO
    const localMax = Math.max(...data);
    const suggestedMax = localMax > 0 ? localMax * 1.15 : 1;

    /* ───────── Card ───────── */
    const card = document.createElement('section');
    card.className = 'card';

    const h = document.createElement('h4');
    h.textContent = p;

    /* ───────── Wrapper estable ───────── */
    const wrapper = document.createElement('div');
    wrapper.style.height = '340px';        // ⬅️ más aire visual
    wrapper.style.position = 'relative';

    const canvas = document.createElement('canvas');
    canvas.style.position = 'absolute';
    canvas.style.inset = '0';

    wrapper.appendChild(canvas);
    card.append(h, wrapper);
    grid.appendChild(card);

    /* ───────── Chart ───────── */
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
        spanGaps: true,
        pointRadius: 3,
        pointHoverRadius: 5
      }],
      {
        ...opcionesTime(kpiActual, `Tendencia · ${p}`),
        scales: {
          x: {
            type: 'time',
            time: { unit: 'day' }
          },
          y: {
            beginAtZero: true,
            suggestedMax,
            ticks: {
              maxTicksLimit: 6
            }
          }
        }
      }
    );
  });

  container.innerHTML = '';
  container.appendChild(grid);
}


/* ======================================================
   NORMALIZACIÓN (días faltantes → 0)
   - labelsISO: ['YYYY-MM-DD', ...] SIEMPRE creciente diario
   - data: valores alineados a labelsISO
====================================================== */
function normalizarSerieContra(labelsISO, series, kpi) {
  const labelsUnicas = [...new Set(labelsISO)].sort();

  const map = new Map();
  for (const p of series || []) {
    const iso = toISODate(p.fecha ?? p.date ?? p.Fecha);
    if (!iso) continue;

    const prev = map.get(iso) ?? 0;
    const val = Number(p[kpi] ?? 0) || 0;
    map.set(iso, prev + val);
  }

  return {
    labelsDate: labelsUnicas.map(iso => new Date(iso)),
    data: labelsUnicas.map(iso => map.get(iso) ?? 0)
  };
}

/* ======================================================
   CALENDARIO (ISO) - POR PASILLO Y GLOBAL
====================================================== */
function generarRangoFechasISO(series) {
  const fechas = (series || [])
    .map(p => toISODate(p.fecha ?? p.date ?? p.Fecha))
    .filter(Boolean)
    .sort();

  if (!fechas.length) return [];

  return rangoISO(fechas[0], fechas[fechas.length - 1]);
}

function generarRangoFechasISO_GLOBAL(data) {
  const all = [];

  Object.values(data || {}).forEach(b => {
    (b.series || []).forEach(p => {
      const iso = toISODate(p.fecha ?? p.date ?? p.Fecha);
      if (iso) all.push(iso);
    });
  });

  all.sort();
  if (!all.length) return [];

  return rangoISO(all[0], all[all.length - 1]);
}

function rangoISO(inicioISO, finISO) {
  const res = [];
  let d = new Date(inicioISO);
  const end = new Date(finISO);

  // Normalizar a medianoche para evitar saltos raros
  d.setHours(0, 0, 0, 0);
  end.setHours(0, 0, 0, 0);

  while (d <= end) {
    res.push(d.toISOString().slice(0, 10));
    d.setDate(d.getDate() + 1);
  }
  return res;
}

function toISODate(x) {
  if (!x) return null;

  // Si ya viene como 'YYYY-MM-DD'
  if (typeof x === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(x)) return x;

  const d = new Date(x);
  if (Number.isNaN(d.getTime())) return null;

  return d.toISOString().slice(0, 10);
}

/* ======================================================
   ESCALA GLOBAL Y (basada en serie NORMALIZADA)
====================================================== */
function calcularMaxGlobalNormalizado(kpi, labelsISO) {
  let max = 0;

  Object.values(dataPorPasillo).forEach(b => {
    const { data } = normalizarSerieContra(labelsISO, b.series, kpi);
    for (const v of data) max = Math.max(max, Number(v) || 0);
  });

  return max || 1;
}

function calcularMinMaxGlobalNormalizado(kpi, labelsISO) {
  let min = Infinity;
  let max = 0;

  Object.values(dataPorPasillo).forEach(b => {
    const { data } = normalizarSerieContra(labelsISO, b.series, kpi);
    for (const v of data) {
      const n = Number(v) || 0;
      if (n > 0) {
        min = Math.min(min, n);
        max = Math.max(max, n);
      }
    }
  });

  if (!isFinite(min)) min = 0;
  if (max === 0) max = 1;

  return { min, max };
}

/* ======================================================
   EXTRACCIÓN DE DATOS
====================================================== */
function extraerDatosPasillos(resultado) {
  const datos = {};
  if (!resultado?.por_pasillo) return datos;

  Object.entries(resultado.por_pasillo).forEach(([k, v]) => {
    const p = normalizarPasillo(k);
    if (!p) return;

    if (Array.isArray(v?.series)) {
      // aquí respetamos el payload tal cual
      datos[p] = { series: v.series };
    }
  });

  return datos;
}

/* ======================================================
   HELPERS UI
====================================================== */
function crearCanvas(container) {
  const c = document.createElement('canvas');
  c.height = 300;
  container.appendChild(c);
  return c;
}

function opcionesTime(kpi, titulo) {
  return {
    plugins: {
      title: { display: true, text: titulo }
    },
    scales: {
      x: {
        type: 'time',
        time: { unit: 'day' }
      },
      y: {
        title: { display: true, text: kpi }
      }
    }
  };
}

function mostrarEstadoEspera() {
  const c = document.getElementById('pasillos-container');
  if (!c) return;
  c.innerHTML = estadoVacio('Esperando datos…');
}

function estadoVacio(txt = 'No hay datos por pasillo.') {
  return `
    <section class="card empty-state">
      <h4>Reporte por pasillos</h4>
      <p class="text-muted">${txt}</p>
    </section>
  `;
}

function normalizarPasillo(p) {
  if (!p) return null;
  const v = String(p).trim().toUpperCase();
  if (PASILLOS_VALIDOS.includes(v)) return v;
  if (/^[1-4]$/.test(v)) return `P${v}`;
  return null;
}

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

function calcularYEscalaInteligente(kpi, labelsISO) {
  const valores = [];

  Object.values(dataPorPasillo).forEach(b => {
    const { data } = normalizarSerieContra(labelsISO, b.series, kpi);
    valores.push(...data.filter(v => v > 0));
  });

  if (!valores.length) return { min: 0, max: 1 };

  valores.sort((a, b) => a - b);

  const p95 = valores[Math.floor(valores.length * 0.95)];
  const max = p95 * 1.15;

  return {
    min: 0,
    max
  };
}
