// ─────────────────────────────
// ESTADO INTERNO
// ─────────────────────────────
let dfOriginal = [];
let kpisFlags = {};


// ─────────────────────────────
// API PÚBLICA
// (equiv. DetalleView.render)
// ─────────────────────────────
export function renderDetalle(resultado) {
  const tab = document.getElementById('tab-detalle');
  tab.innerHTML = '';

  const kpis = resultado.kpis ?? {};
  const resumen = resultado.resumen ?? {};
  const tabla = resultado.tabla ?? [];

  kpisFlags = kpis;

  // ─────────────────────────
  // NORMALIZAR TABLA
  // ─────────────────────────
  let rows = [];

  if (Array.isArray(tabla)) {
    rows = tabla.map(r => ({ ...r }));
  } else {
    rows = [];
  }

  rows = _asegurarColumnas(rows);
  rows = _redondearNumeros(rows);

  dfOriginal = rows.map(r => ({ ...r }));

  // ─────────────────────────
  // TOP: KPIs + FILTRO
  // ─────────────────────────
  const top = document.createElement('div');
  top.className = 'detalle-top';

  if (kpis.importe) {
    const lbl = document.createElement('strong');
    lbl.textContent = `Importe total: $${(resumen.importe_total ?? 0).toFixed(2)}`;
    lbl.style.marginRight = '20px';
    top.appendChild(lbl);
  }

  if (kpis.piezas) {
    const lbl = document.createElement('strong');
    lbl.textContent = `Piezas totales: ${resumen.piezas_total ?? 0}`;
    top.appendChild(lbl);
  }

  // Filtro zona
  const filtroZona = document.createElement('div');
  filtroZona.style.float = 'right';

  const lblZona = document.createElement('label');
  lblZona.textContent = 'Zona: ';
  filtroZona.appendChild(lblZona);

  const selectZona = document.createElement('select');
  filtroZona.appendChild(selectZona);

  top.appendChild(filtroZona);
  tab.appendChild(top);

  // ─────────────────────────
  // TABLA
  // ─────────────────────────
  const tableContainer = document.createElement('div');
  tableContainer.id = 'detalle-table';
  tab.appendChild(tableContainer);

  if (!rows.length) {
    selectZona.innerHTML = `<option>Todas</option>`;
    _renderTabla(rows, tableContainer);
    return;
  }

  // ─────────────────────────
  // CONFIGURAR FILTRO ZONA
  // ─────────────────────────
  const zonas = [...new Set(rows.map(r => String(r.zona ?? '').trim()).filter(z => z))];
  selectZona.innerHTML = `<option>Todas</option>` +
    zonas.map(z => `<option>${z}</option>`).join('');

  selectZona.value = 'Todas';

  selectZona.addEventListener('change', () => {
    _aplicarFiltroZona(selectZona.value, tableContainer);
  });

  _renderTabla(rows, tableContainer);
}


// ─────────────────────────────
// FILTRO POR ZONA
// ─────────────────────────────
function _aplicarFiltroZona(zona, tableContainer) {
  let data;

  if (zona === 'Todas') {
    data = dfOriginal.map(r => ({ ...r }));
  } else {
    data = dfOriginal.filter(r => String(r.zona) === zona);
  }

  data = _asegurarColumnas(data);
  data = _redondearNumeros(data);

  _renderTabla(data, tableContainer);
}


// ─────────────────────────────
// RENDER TABLA
// ─────────────────────────────
function _renderTabla(rows, container) {
  container.innerHTML = '';

  if (!rows.length) {
    container.innerHTML = `<p>No hay datos para mostrar.</p>`;
    return;
  }

  const table = document.createElement('table');
  table.className = 'detalle-table';

  const thead = document.createElement('thead');
  const tbody = document.createElement('tbody');

  const columns = Object.keys(rows[0]);

  // header
  const trHead = document.createElement('tr');
  columns.forEach(col => {
    const th = document.createElement('th');
    th.textContent = col;
    trHead.appendChild(th);
  });
  thead.appendChild(trHead);

  // body
  rows.forEach(row => {
    const tr = document.createElement('tr');
    columns.forEach(col => {
      const td = document.createElement('td');
      td.textContent = row[col] ?? '';
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });

  table.appendChild(thead);
  table.appendChild(tbody);
  container.appendChild(table);
}


// ─────────────────────────────
// HELPERS
// ─────────────────────────────
function _asegurarColumnas(rows) {
  return rows.map(r => {
    const row = { ...r };

    if (!('folio' in row)) row.folio = '';
    if (!('estado' in row)) row.estado = '';
    if (!('zona' in row)) row.zona = '';

    return _ordenarColumnas(row);
  });
}

function _ordenarColumnas(row) {
  const ordered = {};
  ['folio', 'estado', 'zona'].forEach(k => {
    ordered[k] = row[k];
  });

  Object.keys(row).forEach(k => {
    if (!(k in ordered)) ordered[k] = row[k];
  });

  return ordered;
}

function _redondearNumeros(rows) {
  const moneyCols = ['unitario', 'total', 'importe', 'precio', 'subtotal'];
  const intCols = ['cantidad', 'piezas'];

  return rows.map(r => {
    const row = { ...r };

    for (const [k, v] of Object.entries(row)) {
      const kl = k.toLowerCase();

      if (moneyCols.includes(kl)) {
        row[k] = Number(v ?? 0).toFixed(2);
      } else if (intCols.includes(kl)) {
        row[k] = parseInt(v ?? 0, 10);
      }
    }

    return row;
  });
}
