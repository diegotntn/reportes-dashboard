// ─────────────────────────────
// CONSTANTES
// ─────────────────────────────
const MODOS = ['Individual', 'Comparación', 'Todos separados'];
const PASILLOS_VALIDOS = ['P1', 'P2', 'P3', 'P4'];


// ─────────────────────────────
// ESTADO INTERNO
// ─────────────────────────────
let dataPorPasillo = {};
let kpisFlags = {};
let modoActual = MODOS[0];
let pasilloActual = null;
let kpiComparacion = 'importe';


// ─────────────────────────────
// API PÚBLICA
// ─────────────────────────────
export function renderPasillos(resultado) {
  const raw = resultado.por_pasillo ?? {};
  kpisFlags = resultado.kpis ?? {};

  // Normalizar pasillos
  dataPorPasillo = {};
  for (const [key, bloque] of Object.entries(raw)) {
    const p = _normalizarPasillo(key);
    if (p) dataPorPasillo[p] = bloque;
  }

  const pasillos = PASILLOS_VALIDOS.filter(p => p in dataPorPasillo);
  const tab = document.getElementById('tab-pasillos');
  tab.innerHTML = '';

  if (!pasillos.length) {
    tab.innerHTML = `<p>No hay datos para mostrar.</p>`;
    return;
  }

  if (!pasilloActual || !pasillos.includes(pasilloActual)) {
    pasilloActual = pasillos[0];
  }

  _normalizarKpiComparacion();

  // ─────────────────────────
  // Barra superior
  // ─────────────────────────
  const top = document.createElement('div');
  top.className = 'pasillos-top';

  top.appendChild(_label('Modo:'));
  top.appendChild(_select(MODOS, modoActual, v => {
    modoActual = v;
    _renderActual();
  }));

  top.appendChild(_label('Pasillo:'));
  top.appendChild(_select(pasillos, pasilloActual, v => {
    pasilloActual = v;
    _renderActual();
  }));

  top.appendChild(_label('KPI:'));
  top.appendChild(_select(_kpisDisponibles(), kpiComparacion, v => {
    kpiComparacion = v;
    _renderActual();
  }));

  tab.appendChild(top);

  const container = document.createElement('div');
  container.id = 'pasillos-container';
  tab.appendChild(container);

  _renderActual();
}


// ─────────────────────────────
// RENDER SEGÚN MODO
// ─────────────────────────────
function _renderActual() {
  const container = document.getElementById('pasillos-container');
  container.innerHTML = '';

  if (modoActual === 'Individual') {
    _renderIndividual(container);
  } else if (modoActual === 'Comparación') {
    _renderComparacion(container);
  } else {
    _renderTodos(container);
  }
}


// ─────────────────────────────
// MODO INDIVIDUAL
// ─────────────────────────────
function _renderIndividual(container) {
  const bloque = dataPorPasillo[pasilloActual];
  if (!bloque || !Array.isArray(bloque.series)) {
    container.innerHTML = `<p>No hay datos para mostrar.</p>`;
    return;
  }

  const series = bloque.series;
  if (!series.length) {
    container.innerHTML = `<p>No hay datos para mostrar.</p>`;
    return;
  }

  // KPIs
  const kpis = document.createElement('div');
  kpis.className = 'kpis';
  _renderKpisRow(kpis, bloque.resumen);
  container.appendChild(kpis);

  // Gráfica
  const x = series.map(p => p.fecha);

  const chartDiv = document.createElement('div');
  container.appendChild(chartDiv);

  Plotly.newPlot(chartDiv, [{
    x,
    y: series.map(p => p[kpiComparacion] ?? 0),
    type: 'scatter',
    mode: 'lines+markers',
    name: pasilloActual
  }], {
    title: `Tendencia · ${pasilloActual}`
  });
}


// ─────────────────────────────
// MODO COMPARACIÓN
// ─────────────────────────────
function _renderComparacion(container) {
  if (!kpisFlags[kpiComparacion]) {
    container.innerHTML = `<p>Activa al menos un KPI para comparar.</p>`;
    return;
  }

  const traces = [];

  PASILLOS_VALIDOS.forEach(p => {
    const bloque = dataPorPasillo[p];
    if (!bloque || !Array.isArray(bloque.series) || !bloque.series.length) return;

    traces.push({
      x: bloque.series.map(pt => pt.fecha),
      y: bloque.series.map(pt => pt[kpiComparacion] ?? 0),
      type: 'scatter',
      mode: 'lines+markers',
      name: p
    });
  });

  if (!traces.length) {
    container.innerHTML = `<p>No hay datos suficientes para comparar.</p>`;
    return;
  }

  const chartDiv = document.createElement('div');
  container.appendChild(chartDiv);

  Plotly.newPlot(chartDiv, traces, {
    title: `Comparación · ${kpiComparacion.toUpperCase()} (P1–P4)`,
    legend: { orientation: 'h' }
  });
}


// ─────────────────────────────
// MODO TODOS SEPARADOS
// ─────────────────────────────
function _renderTodos(container) {
  const grid = document.createElement('div');
  grid.className = 'pasillos-grid';

  PASILLOS_VALIDOS.forEach(p => {
    const bloque = dataPorPasillo[p];
    if (!bloque || !Array.isArray(bloque.series) || !bloque.series.length) return;

    const card = document.createElement('fieldset');
    card.innerHTML = `<legend>Pasillo ${p}</legend>`;

    const kpis = document.createElement('div');
    kpis.className = 'kpis';
    _renderKpisRow(kpis, bloque.resumen);
    card.appendChild(kpis);

    const chartDiv = document.createElement('div');
    card.appendChild(chartDiv);

    Plotly.newPlot(chartDiv, [{
      x: bloque.series.map(pt => pt.fecha),
      y: bloque.series.map(pt => pt[kpiComparacion] ?? 0),
      type: 'scatter',
      mode: 'lines+markers'
    }], {
      title: `Tendencia · ${p}`
    });

    grid.appendChild(card);
  });

  if (!grid.children.length) {
    container.innerHTML = `<p>No hay datos para mostrar.</p>`;
    return;
  }

  container.appendChild(grid);
}


// ─────────────────────────────
// KPIs
// ─────────────────────────────
function _renderKpisRow(parent, resumen = {}) {
  parent.innerHTML = '';

  if (kpisFlags.importe) parent.appendChild(_kpi('Importe', resumen.importe ?? 0, '$'));
  if (kpisFlags.piezas) parent.appendChild(_kpi('Piezas', resumen.piezas ?? 0));
  if (kpisFlags.devoluciones) parent.appendChild(_kpi('Devoluciones', resumen.devoluciones ?? 0));

  if (!parent.children.length) {
    parent.innerHTML = `<p>No hay KPIs activos.</p>`;
  }
}


// ─────────────────────────────
// HELPERS UI / DATOS
// ─────────────────────────────
function _normalizarPasillo(p) {
  if (p == null) return null;
  p = String(p).trim().toUpperCase();
  if (PASILLOS_VALIDOS.includes(p)) return p;
  if (/^[1-4]$/.test(p)) return `P${p}`;
  return null;
}

function _kpisDisponibles() {
  return ['importe', 'piezas', 'devoluciones'].filter(k => kpisFlags[k]);
}

function _normalizarKpiComparacion() {
  const disp = _kpisDisponibles();
  if (!disp.length) return;
  if (!disp.includes(kpiComparacion)) {
    kpiComparacion = disp[0];
  }
}

function _kpi(title, value, prefix = '') {
  const div = document.createElement('div');
  div.className = 'kpi';
  div.innerHTML = `<strong>${title}</strong><div>${prefix}${value}</div>`;
  return div;
}

function _label(text) {
  const l = document.createElement('label');
  l.textContent = text;
  l.style.margin = '0 6px';
  return l;
}

function _select(values, current, onChange) {
  const s = document.createElement('select');
  values.forEach(v => {
    const o = document.createElement('option');
    o.value = v;
    o.textContent = v;
    s.appendChild(o);
  });
  s.value = current;
  s.addEventListener('change', () => onChange(s.value));
  return s;
}
