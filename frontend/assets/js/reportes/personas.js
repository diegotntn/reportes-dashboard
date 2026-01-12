// ─────────────────────────────
// ESTADO INTERNO
// ─────────────────────────────
let dataPorPersona = {};
let kpisFlags = {};
let personaSeleccionada = null;


// ─────────────────────────────
// API PÚBLICA
// ─────────────────────────────
export function renderPersonas(resultado) {
  dataPorPersona = resultado.por_persona ?? {};
  kpisFlags = resultado.kpis ?? {};

  const personas = Object.keys(dataPorPersona).sort();
  const tab = document.getElementById('tab-personas');
  tab.innerHTML = '';

  if (!personas.length) {
    _clearAll(tab);
    return;
  }

  // ─────────────────────────
  // Selector de persona
  // ─────────────────────────
  const top = document.createElement('div');
  top.className = 'persona-selector';

  const label = document.createElement('label');
  label.textContent = 'Persona: ';
  label.style.marginRight = '6px';

  const select = document.createElement('select');
  select.style.minWidth = '220px';

  personas.forEach(p => {
    const option = document.createElement('option');
    option.value = p;
    option.textContent = p;
    select.appendChild(option);
  });

  if (!personaSeleccionada || !personas.includes(personaSeleccionada)) {
    personaSeleccionada = personas[0];
  }

  select.value = personaSeleccionada;

  select.addEventListener('change', () => {
    personaSeleccionada = select.value;
    _renderPersona(personaSeleccionada);
  });

  top.appendChild(label);
  top.appendChild(select);
  tab.appendChild(top);

  // ─────────────────────────
  // Contenedores
  // ─────────────────────────
  const kpiContainer = document.createElement('div');
  kpiContainer.id = 'personas-kpis';
  kpiContainer.className = 'kpis';

  const chartContainer = document.createElement('div');
  chartContainer.id = 'personas-chart';
  chartContainer.style.marginTop = '12px';

  tab.appendChild(kpiContainer);
  tab.appendChild(chartContainer);

  _renderPersona(personaSeleccionada);
}


// ─────────────────────────────
// Render de persona individual
// ─────────────────────────────
function _renderPersona(persona) {
  const data = dataPorPersona[persona];
  const kpiContainer = document.getElementById('personas-kpis');
  const chartContainer = document.getElementById('personas-chart');

  kpiContainer.innerHTML = '';
  chartContainer.innerHTML = '';

  if (!data || !data.series) return;

  const series = data.series;
  const resumen = data.resumen ?? {};

  if (!series.length) return;

  // ─────────────────────────
  // KPIs
  // ─────────────────────────
  if (kpisFlags.importe) {
    kpiContainer.appendChild(
      _kpi('Importe', resumen.importe ?? 0, '$')
    );
  }

  if (kpisFlags.piezas) {
    kpiContainer.appendChild(
      _kpi('Piezas', resumen.piezas ?? 0)
    );
  }

  if (kpisFlags.devoluciones) {
    kpiContainer.appendChild(
      _kpi('Devoluciones', resumen.devoluciones ?? 0)
    );
  }

  // ─────────────────────────
  // Gráfica (Plotly)
  // ─────────────────────────
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

  Plotly.newPlot(chartContainer, traces, {
    title: `Tendencia · ${persona}`,
    margin: { t: 40 },
    legend: { orientation: 'h' }
  });
}


// ─────────────────────────────
// KPI helper
// ─────────────────────────────
function _kpi(title, value, prefix = '') {
  const div = document.createElement('div');
  div.className = 'kpi';

  div.innerHTML = `
    <strong>${title}</strong>
    <div>${prefix}${value}</div>
  `;

  return div;
}


// ─────────────────────────────
// Limpieza total
// ─────────────────────────────
function _clearAll(tab) {
  tab.innerHTML = `<p>No hay datos para mostrar</p>`;
}
