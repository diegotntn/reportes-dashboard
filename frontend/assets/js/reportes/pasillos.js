/* ======================================================
   PasillosView Controller
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
    .filter(k => dataPorPasillo[pasilloActual].series.some(pt => Number.isFinite(pt[k])));

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
   AGRUPAR NORMALIZADO
====================================================== */
function getAgrupar() {
  const raw = String(ultimoResultado?.rango?.agrupar ?? 'Dia').toLowerCase();
  if (raw.startsWith('mes')) return 'Mes';
  if (raw.startsWith('sem')) return 'Semana';
  return 'Dia';
}

/* ======================================================
   CALENDARIO MAESTRO
====================================================== */
function calendarioDesdeFiltro() {
  const inicio = ultimoResultado?.rango?.inicio;
  const fin = ultimoResultado?.rango?.fin;
  const agrupar = getAgrupar();

  if (!inicio || !fin) return { labelsKey: [], labelsDate: [], unit: 'day', agrupar };

  if (agrupar === 'Mes') {
    const labelsKey = rangoMensualKey(inicio, fin);
    return { labelsKey, labelsDate: labelsKey.map(keyMesToDate), unit: 'month', agrupar };
  }

  if (agrupar === 'Semana') {
    const labelsKey = rangoSemanalKey(inicio, fin);
    return { labelsKey, labelsDate: labelsKey.map(keySemanaToDate), unit: 'week', agrupar };
  }

  const labelsKey = rangoDiarioKey(inicio, fin);
  return { labelsKey, labelsDate: labelsKey.map(keyDiaToDate), unit: 'day', agrupar };
}

/* ======================================================
   GRÁFICAS - CORREGIDO
====================================================== */
function renderIndividual(container) {
  const bloque = dataPorPasillo[pasilloActual];
  if (!bloque) return;

  const { labelsKey, labelsDate, unit, agrupar } = calendarioDesdeFiltro();
  if (!labelsKey.length) return;

  const data = normalizarSerieContra(labelsKey, bloque.series, kpiActual, agrupar);
  
  // Crear serie en formato compatible con charts.js
  const serie = labelsKey.map((key, i) => ({
    key: key,
    label: formatearLabel(key, agrupar),
    fecha: labelsDate[i],
    kpis: {
      importe: data[i] || 0,
      piezas: 0,
      devoluciones: 0
    }
  }));

  const canvas = crearCanvas(container);

  // Llamar CORRECTAMENTE a renderLineChart (API NUEVA)
  renderLineChart(canvas, {
    periodo: agrupar.toLowerCase(),
    series: [{  // ¡IMPORTANTE: 'series' (plural) y es un array!
      label: pasilloActual,
      color: COLORES[0],
      bg: COLORES_BG[0],
      serie: serie  // ¡Y aquí dentro es 'serie' (singular)!
    }]
  }, opcionesTime(kpiActual, `Tendencia · ${pasilloActual}`, unit));
}
function renderComparacion(container) {
  const { labelsKey, labelsDate, unit, agrupar } = calendarioDesdeFiltro();
  if (!labelsKey.length) return;

  console.log('[PASILLOS][Comparación] labels:', labelsKey.length);

  const series = PASILLOS_VALIDOS
    .filter(p => dataPorPasillo[p])
    .map((p, i) => {
      const bloque = dataPorPasillo[p];

      const data = normalizarSerieContra(
        labelsKey,
        bloque.series,
        kpiActual,
        agrupar
      );

      console.log(`[PASILLOS][Comparación] ${p} data:`, data.slice(0, 6));

      const serie = labelsKey.map((key, idx) => ({
        key,
        label: formatearLabel(key, agrupar),
        fecha: labelsDate[idx],
        kpis: {
          importe: data[idx] || 0,
          piezas: 0,
          devoluciones: 0
        }
      }));

      return {
        label: p,
        color: COLORES[i],
        bg: COLORES_BG[i],
        fill: false,
        serie
      };
    });

  if (!series.length) {
    console.warn('[PASILLOS][Comparación] sin series');
    return;
  }

  const canvas = crearCanvas(container);

  renderLineChart(
    canvas,
    {
      periodo: agrupar.toLowerCase(),
      series
    },
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

    const data = normalizarSerieContra(
      labelsKey,
      bloque.series,
      kpiActual,
      agrupar
    );

    console.log(`[PASILLOS][Todos] ${p} data:`, data.slice(0, 6));

    const serie = labelsKey.map((key, idx) => ({
      key,
      label: formatearLabel(key, agrupar),
      fecha: labelsDate[idx],
      kpis: {
        importe: data[idx] || 0,
        piezas: 0,
        devoluciones: 0
      }
    }));

    const card = document.createElement('section');
    card.className = 'card';

    const h = document.createElement('h4');
    h.textContent = p;

    const canvas = document.createElement('canvas');
    canvas.style.width = '100%';
    canvas.style.height = '280px';

    card.append(h, canvas);
    grid.appendChild(card);

    renderLineChart(
      canvas,
      {
        periodo: agrupar.toLowerCase(),
        series: [{
          label: p,
          color: COLORES[i],
          bg: COLORES_BG[i],
          fill: false,
          serie
        }]
      },
      {
        ...opcionesTime(kpiActual, `Tendencia · ${p}`, unit),
        plugins: {
          legend: { display: false }
        }
      }
    );
  });

  container.appendChild(grid);
}


/* ======================================================
   FUNCIÓN PARA FORMATEAR LABELS
====================================================== */
function formatearLabel(key, agrupar) {
  if (agrupar === 'Dia') {
    const [y, m, d] = key.split('-');
    return `${d}/${m}/${y}`;
  }
  if (agrupar === 'Mes') {
    const [y, m] = key.split('-');
    return `${m}/${y}`;
  }
  if (agrupar === 'Semana') {
    const [y, w] = key.split('-W');
    return `Sem ${w} ${y}`;
  }
  return key;
}

/* ======================================================
   OPCIONES TIME COMPLETA
====================================================== */
function opcionesTime(kpi, titulo, unit) {
  return {
    aspectRatio: 2.5,
    plugins: {
      title: {
        display: true,
        text: titulo,
        font: {
          size: 16,
          weight: 'bold'
        }
      }
    },
    scales: {
      x: {
        type: 'time',
        time: {
          unit: unit,
          displayFormats: {
            day: 'dd/MM',
            week: "'Sem' w",
            month: 'MMM yyyy'
          }
        },
        title: {
          display: true,
          text: 'Fecha'
        }
      },
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: kpi.toUpperCase()
        }
      }
    }
  };
}

/* ======================================================
   NORMALIZACIÓN DE SERIES (MANTENER IGUAL)
====================================================== */
function normalizarSerieContra(labelsKey, series, kpi, agrupar) {
  const map = new Map();

  for (const p of series || []) {
    const key = normalizarClaveSegunAgrupar(p.fecha, agrupar);
    if (!key) continue;

    const val = Number(p[kpi]);
    map.set(key, (map.get(key) ?? 0) + (Number.isFinite(val) ? val : 0));
  }

  return labelsKey.map(k => map.get(k) ?? 0);
}

function normalizarClaveSegunAgrupar(x, agrupar) {
  const iso = extraerFechaISO(x);
  if (!iso) return null;

  if (agrupar === 'Dia') return iso;
  if (agrupar === 'Mes') return iso.slice(0, 7);

  const d = keyDiaToDate(iso);
  return `${isoWeekYear(d)}-W${String(isoWeekNumber(d)).padStart(2, '0')}`;
}

function extraerFechaISO(x) {
  if (!x) return null;
  if (typeof x === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(x)) return x;
  const d = new Date(x);
  return isNaN(d) ? null : fmtDia(d);
}

/* ======================================================
   RANGOS Y HELPERS FECHA (MANTENER IGUAL)
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

function keyDiaToDate(k) { const [y, m, d] = k.split('-').map(Number); return new Date(y, m - 1, d); }
function keyMesToDate(k) { const [y, m] = k.split('-').map(Number); return new Date(y, m - 1, 1); }
function keySemanaToDate(k) { const [y, w] = k.split('-W').map(Number); return isoWeekToDate(y, w); }

function startOfISOMonday(d) {
  const r = new Date(d); r.setDate(r.getDate() - ((r.getDay() + 6) % 7)); return r;
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

function fmtDia(d) { return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`; }

/* ======================================================
   UI
====================================================== */
function crearCanvas(container) {
  const canvas = document.createElement('canvas');
  canvas.style.width = '100%';
  canvas.style.height = '400px';
  canvas.style.maxHeight = '500px';
  container.appendChild(canvas);
  return canvas;
}

function mostrarEstadoEspera() {
  const container = document.getElementById('pasillos-container');
  if (container) container.innerHTML = estadoVacio('Esperando datos…');
}

function estadoVacio(t = 'No hay datos por pasillo.') {
  return `<section class="card empty-state"><h4>Reporte por pasillos</h4><p>${t}</p></section>`;
}

/* ======================================================
   DATOS
====================================================== */
function extraerDatosPasillos(res) {
  const o = {};
  Object.entries(res?.por_pasillo || {}).forEach(([k, v]) => {
    const p = normalizarPasillo(k);
    if (p && Array.isArray(v?.series)) {
      o[p] = { 
        series: v.series.map(item => ({
          ...item,
          fecha: item.fecha || item.key || ''
        }))
      };
    }
  });
  return o;
}

function normalizarPasillo(p) {
  const v = String(p).toUpperCase();
  if (PASILLOS_VALIDOS.includes(v)) return v;
  if (/^[1-4]$/.test(v)) return `P${v}`;
  return null;
}

/* ======================================================
   CONTROLES
====================================================== */
function label(t) { 
  const l = document.createElement('label'); 
  l.textContent = t; 
  l.style.margin = '0 6px';
  l.style.fontWeight = '500';
  l.style.color = '#374151';
  return l; 
}

function select(vs, c, cb) { 
  const s = document.createElement('select'); 
  s.style.margin = '0 12px 0 4px';
  s.style.padding = '6px 12px';
  s.style.border = '1px solid #d1d5db';
  s.style.borderRadius = '4px';
  s.style.backgroundColor = 'white';
  
  vs.forEach(v => s.append(new Option(v, v))); 
  s.value = c; 
  s.onchange = () => cb(s.value); 
  return s; 
}