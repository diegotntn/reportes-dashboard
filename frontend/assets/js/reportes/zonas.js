// ─────────────────────────────
// ESTADO INTERNO
// ─────────────────────────────
let dataPorZona = {};
let kpisFlags = {};
let zonasVisibles = {};


// ─────────────────────────────
// API PÚBLICA
// ─────────────────────────────
export function renderZonas(resultado) {
  dataPorZona = resultado.por_zona ?? {};
  kpisFlags = resultado.kpis ?? {};

  const zonas = Object.keys(dataPorZona).sort();
  const tab = document.getElementById('tab-zonas');
  tab.innerHTML = '';

  if (!zonas.length) {
    tab.innerHTML = `<p>No hay datos para mostrar</p>`;
    return;
  }

  // ─────────────────────────
  // Selector de zonas
  // ─────────────────────────
  const selector = document.createElement('fieldset');
  selector.innerHTML = `<legend>Zonas visibles</legend>`;

  zonasVisibles = {};

  zonas.forEach(zona => {
    zonasVisibles[zona] = true;

    const label = document.createElement('label');
    label.style.marginRight = '12px';

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.checked = true;

    checkbox.addEventListener('change', () => {
      zonasVisibles[zona] = checkbox.checked;
      _refrescarZonas();
    });

    label.appendChild(checkbox);
    label.append(` ${zona}`);
    selector.appendChild(label);
  });

  const btnTodas = document.createElement('button');
  btnTodas.textContent = 'Todas';
  btnTodas.onclick = _seleccionarTodas;

  const btnNinguna = document.createElement('button');
  btnNinguna.textContent = 'Ninguna';
  btnNinguna.onclick = _deseleccionarTodas;

  selector.appendChild(btnNinguna);
  selector.appendChild(btnTodas);
  tab.appendChild(selector);

  // ─────────────────────────
  // Contenedor de zonas
  // ─────────────────────────
  const container = document.createElement('div');
  container.id = 'zonas-container';
  container.className = 'scroll';
  tab.appendChild(container);

  _refrescarZonas();
}


// ─────────────────────────────
// RENDER INTERNO
// ─────────────────────────────
function _refrescarZonas() {
  const container = document.getElementById('zonas-container');
  container.innerHTML = '';

  const visibles = Object.entries(zonasVisibles)
    .filter(([, v]) => v)
    .map(([z]) => z);

  if (!visibles.length) {
    container.innerHTML = `<p>Selecciona al menos una zona</p>`;
    return;
  }

  visibles.forEach(zona => {
    _renderZona(zona, dataPorZona[zona]);
  });
}

function _seleccionarTodas() {
  Object.keys(zonasVisibles).forEach(z => zonasVisibles[z] = true);
  _refrescarZonas();
}

function _deseleccionarTodas() {
  Object.keys(zonasVisibles).forEach(z => zonasVisibles[z] = false);
  _refrescarZonas();
}


// ─────────────────────────────
// ZONA INDIVIDUAL
// ─────────────────────────────
function _renderZona(zona, data) {
  if (!data || !data.series) return;

  const series = data.series;
  const resumen = data.resumen ?? {};

  if (!series.length) return;

  const container = document.getElementById('zonas-container');

  const frame = document.createElement('fieldset');
  frame.style.margin = '12px';
  frame.innerHTML = `<legend>Zona: ${zona}</legend>`;

  // ───────── KPIs ─────────
  const kpis = document.createElement('div');
  kpis.className = 'kpis';

  if (kpisFlags.importe) {
    kpis.appendChild(_kpi('Importe', resumen.importe, '$'));
  }

  if (kpisFlags.piezas) {
    kpis.appendChild(_kpi('Piezas', resumen.piezas));
  }

  if (kpisFlags.devoluciones) {
    kpis.appendChild(_kpi('Devoluciones', resumen.devoluciones));
  }

  frame.appendChild(kpis);

  // ───────── Gráfica ─────────
  const x = series.map(p => p.fecha);

  const traces = [];

  if (kpisFlags.importe) {
    traces.push({
      x,
      y: series.map(p => p.importe ?? 0),
      name: 'Importe',
      type: 'scatter'
    });
  }

  if (kpisFlags.piezas) {
    traces.push({
      x,
      y: series.map(p => p.piezas ?? 0),
      name: 'Piezas',
      type: 'scatter'
    });
  }

  if (kpisFlags.devoluciones) {
    traces.push({
      x,
      y: series.map(p => p.devoluciones ?? 0),
      name: 'Devoluciones',
      type: 'scatter'
    });
  }

  const chartDiv = document.createElement('div');
  frame.appendChild(chartDiv);

  Plotly.newPlot(chartDiv, traces, {
    title: `Tendencia · Zona ${zona}`,
    margin: { t: 40 },
    legend: { orientation: 'h' }
  });

  container.appendChild(frame);
}


// ─────────────────────────────
// KPI UI
// ─────────────────────────────
function _kpi(title, value, prefix = '') {
  const div = document.createElement('div');
  div.className = 'kpi';
  div.innerHTML = `
    <strong>${title}</strong>
    <div>${prefix}${value ?? 0}</div>
  `;
  return div;
}
