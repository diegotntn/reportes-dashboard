/* ======================================================
   PasillosView Controller - VERSIÓN CON DIAGNÓSTICO
   =======================
   RESPONSABILIDADES:
   - Renderizar información por pasillo
   - Permitir comparación visual
   - Gestionar modo de visualización (UI)

   NO HACE:
   - Fetch
   - Backend
   - Timing hacks
====================================================== */

console.log('🟢 PasillosView cargado - VERSIÓN DIAGNÓSTICO');

/* ======================================================
   CONSTANTES
====================================================== */
const MODOS = ['Individual', 'Comparación', 'Todos separados'];
const PASILLOS_VALIDOS = ['P1', 'P2', 'P3', 'P4'];

/* ======================================================
   ESTADO LOCAL
====================================================== */
let dataPorPasillo = {};
let modoActual = MODOS[0];
let pasilloActual = null;
let kpiActual = 'importe';
let ultimoResultado = null;
let diagnosticoActivado = true; // Cambiar a false una vez resuelto

/* ======================================================
   EVENTOS GLOBALES
====================================================== */

// Llegan datos (aunque pasillos no esté visible)
window.addEventListener('reportes:actualizados', e => {
  console.log('📊 [PasillosView] Datos actualizados recibidos');
  console.log('📊 Evento completo:', e);
  console.log('📊 e.detail:', e.detail);
  ultimoResultado = e.detail;
  
  if (diagnosticoActivado) {
    console.log('📊 Ultimo resultado almacenado:', ultimoResultado);
    console.log('📊 ¿Tiene por_pasillo?:', ultimoResultado?.por_pasillo ? 'SÍ' : 'NO');
    if (ultimoResultado?.por_pasillo) {
      console.log('📊 Claves en por_pasillo:', Object.keys(ultimoResultado.por_pasillo));
    }
  }
});

// Vista HTML ya montada → ahora SÍ se puede renderizar
window.addEventListener('reportes:vista-montada', e => {
  console.log('🎯 [PasillosView] Evento vista-montada recibido');
  console.log('🎯 Detalles del evento:', e.detail);
  
  if (e.detail?.tab !== 'pasillos') {
    console.log('🎯 Ignorando evento - no es para pestaña pasillos');
    return;
  }

  console.log('✅ [PasillosView] vista-montada para pestaña "pasillos"');
  
  if (diagnosticoActivado) {
    console.log('🔍 DIAGNÓSTICO INICIADO =======================');
    console.log('🔍 1. Verificando estado de datos...');
    console.log('🔍    ¿Hay ultimoResultado?:', ultimoResultado ? 'SÍ' : 'NO');
    console.log('🔍    ¿Tiene por_pasillo?:', ultimoResultado?.por_pasillo ? 'SÍ' : 'NO');
    
    console.log('🔍 2. Verificando DOM...');
    console.log('🔍    ¿Existe tab-pasillos?:', document.getElementById('tab-pasillos') ? 'SÍ' : 'NO');
    
    const tab = document.getElementById('tab-pasillos');
    if (tab) {
      console.log('🔍    InnerHTML de tab-pasillos:');
      console.log(tab.innerHTML);
      console.log('🔍    Longitud HTML:', tab.innerHTML.length);
      console.log('🔍    ¿Tiene clase pasillos-controls?:', tab.querySelector('.pasillos-controls') ? 'SÍ' : 'NO');
      console.log('🔍    ¿Tiene id pasillos-container?:', tab.querySelector('#pasillos-container') ? 'SÍ' : 'NO');
    }
    
    console.log('🔍 3. Verificando toda la página...');
    console.log('🔍    Elementos con clase "pasillos-controls":', document.querySelectorAll('.pasillos-controls').length);
    console.log('🔍    Elementos con id "pasillos-container":', document.querySelectorAll('#pasillos-container').length);
    
    console.log('🔍 4. Mostrando estructura del DOM completo...');
    console.log('🔍    body.innerHTML (primeros 500 chars):', document.body.innerHTML.substring(0, 500));
  }

  if (!ultimoResultado) {
    console.warn('⚠️ No hay datos para pasillos aún - esperando evento reportes:actualizados');
    return;
  }

  renderSeguro();
});

/* ======================================================
   RENDER SEGURO CON REINTENTOS INTELIGENTES
====================================================== */
function renderSeguro() {
  console.log('🔄 [PasillosView] Iniciando renderSeguro()');
  
  if (diagnosticoActivado) {
    console.log('🔄 Estado al inicio de renderSeguro:');
    console.log('🔄   ultimoResultado:', ultimoResultado);
    console.log('🔄   dataPorPasillo:', dataPorPasillo);
  }
  
  const tab = document.getElementById('tab-pasillos');
  if (!tab) {
    console.error('❌ CRÍTICO: tab-pasillos no existe en el DOM');
    console.error('❌ Todos los elementos con "tab-" en el documento:');
    document.querySelectorAll('[id^="tab-"]').forEach(el => {
      console.error(`   - ${el.id}`);
    });
    return;
  }

  console.log('✅ tab-pasillos encontrado');
  
  // Buscar elementos con múltiples estrategias
  let controls = tab.querySelector('.pasillos-controls');
  let container = tab.querySelector('#pasillos-container');
  
  console.log('🔎 Buscando elementos dentro de tab-pasillos...');
  console.log('🔎 controls (primer intento):', controls);
  console.log('🔎 container (primer intento):', container);
  
  // Si no los encuentra, intentar buscarlos en todo el documento
  if (!controls) {
    controls = document.querySelector('.pasillos-controls');
    console.log('🔎 controls (búsqueda global):', controls);
  }
  
  if (!container) {
    container = document.getElementById('pasillos-container');
    console.log('🔎 container (búsqueda global):', container);
  }
  
  // Si aún no los encuentra, crear elementos temporales
  if (!controls || !container) {
    console.warn('⚠️ Elementos no encontrados. Creando elementos temporales...');
    
    if (!controls) {
      controls = document.createElement('div');
      controls.className = 'pasillos-controls';
      tab.appendChild(controls);
      console.log('✅ controls creado temporalmente');
    }
    
    if (!container) {
      container = document.createElement('div');
      container.id = 'pasillos-container';
      tab.appendChild(container);
      console.log('✅ container creado temporalmente');
    }
  }

  console.log('✅ Elementos listos para renderizar');
  console.log('✅ controls:', controls);
  console.log('✅ container:', container);
  
  renderPasillos(ultimoResultado, controls, container);
}

/* ======================================================
   RENDER PRINCIPAL
====================================================== */
function renderPasillos(resultado, controls, container) {
  console.log('🧪 [PasillosView] Iniciando renderPasillos()');
  
  if (diagnosticoActivado) {
    console.log('🧪 Parámetros recibidos:');
    console.log('🧪   resultado:', resultado);
    console.log('🧪   controls:', controls);
    console.log('🧪   container:', container);
    console.log('🧪   controls.innerHTML (antes):', controls.innerHTML.substring(0, 100));
    console.log('🧪   container.innerHTML (antes):', container.innerHTML.substring(0, 100));
  }

  const raw = resultado?.por_pasillo ?? {};
  dataPorPasillo = {};

  console.log('📦 Datos brutos (por_pasillo):', raw);
  console.log('📦 Claves en raw:', Object.keys(raw));

  Object.entries(raw).forEach(([key, bloque]) => {
    console.log(`📦 Procesando pasillo "${key}":`, bloque);
    const p = normalizarPasillo(key);
    console.log(`📦 Pasillo normalizado: "${key}" -> "${p}"`);
    
    if (p && bloque?.series?.length) {
      dataPorPasillo[p] = bloque;
      console.log(`✅ Pasillo "${p}" agregado con ${bloque.series.length} registros`);
    } else {
      console.log(`❌ Pasillo "${p}" descartado - ¿bloque?: ${!!bloque}, ¿series?: ${bloque?.series?.length || 0}`);
    }
  });

  const pasillos = PASILLOS_VALIDOS.filter(p => dataPorPasillo[p]);
  
  console.log('📊 Pasillos válidos encontrados:', pasillos);
  console.log('📊 dataPorPasillo final:', dataPorPasillo);

  controls.innerHTML = '';
  limpiarPlotly(container);
  container.innerHTML = '';

  if (!pasillos.length) {
    console.log('📭 No hay datos de pasillos - mostrando estado vacío');
    container.innerHTML = `
      <section class="card empty-state">
        <h4>Reporte por pasillos</h4>
        <p class="text-muted">
          No hay datos por pasillo para el periodo seleccionado.
        </p>
        <p class="text-small">
          Datos recibidos: ${ultimoResultado ? 'SÍ' : 'NO'}<br>
          Claves en por_pasillo: ${Object.keys(raw).join(', ') || '(ninguna)'}
        </p>
      </section>
    `;
    return;
  }

  if (!pasilloActual || !pasillos.includes(pasilloActual)) {
    pasilloActual = pasillos[0];
    console.log(`🎯 Pasillo actual establecido a: ${pasilloActual}`);
  }

  const kpisDisponibles = ['importe', 'piezas', 'devoluciones']
    .filter(k =>
      dataPorPasillo[pasilloActual].series.some(pt => pt[k] != null)
    );

  console.log(`📈 KPIs disponibles para ${pasilloActual}:`, kpisDisponibles);

  if (!kpisDisponibles.includes(kpiActual)) {
    kpiActual = kpisDisponibles[0];
    console.log(`📈 KPI actual establecido a: ${kpiActual}`);
  }

  /* ───────── Controles UI ───────── */
  console.log('🎛️ Creando controles UI...');
  
  controls.append(
    label('Modo:'),
    select(MODOS, modoActual, v => {
      console.log(`🎛️ Modo cambiado a: ${v}`);
      modoActual = v;
      renderActual(container);
    }),
    label('Pasillo:'),
    select(pasillos, pasilloActual, v => {
      console.log(`🎛️ Pasillo cambiado a: ${v}`);
      pasilloActual = v;
      renderActual(container);
    }),
    label('KPI:'),
    select(kpisDisponibles, kpiActual, v => {
      console.log(`🎛️ KPI cambiado a: ${v}`);
      kpiActual = v;
      renderActual(container);
    })
  );

  console.log('🎛️ Controles creados, iniciando renderActual...');
  renderActual(container);
}

/* ======================================================
   RENDER SEGÚN MODO
====================================================== */
function renderActual(container) {
  console.log(`🎨 [PasillosView] renderActual() - Modo: ${modoActual}`);
  
  limpiarPlotly(container);
  container.innerHTML = '';

  if (modoActual === 'Individual') {
    console.log('🎨 Modo Individual seleccionado');
    renderIndividual(container);
  } else if (modoActual === 'Comparación') {
    console.log('🎨 Modo Comparación seleccionado');
    renderComparacion(container);
  } else {
    console.log('🎨 Modo Todos separados seleccionado');
    renderTodos(container);
  }
  
  console.log('🎨 Render completado');
}

/* ======================================================
   MODOS DE VISUALIZACIÓN
====================================================== */
function renderIndividual(container) {
  console.log(`📊 renderIndividual() para pasillo: ${pasilloActual}`);
  
  const bloque = dataPorPasillo[pasilloActual];
  if (!bloque) {
    console.error(`❌ No hay datos para pasillo ${pasilloActual}`);
    return;
  }

  console.log(`📊 Datos para ${pasilloActual}:`, bloque);
  console.log(`📊 KPI seleccionado: ${kpiActual}`);
  console.log(`📊 Valores KPI:`, bloque.series.map(p => p[kpiActual] ?? 0));

  const chart = document.createElement('div');
  chart.className = 'plotly-chart';
  container.appendChild(chart);

  console.log('📊 Creando gráfico Plotly...');
  
  try {
    Plotly.newPlot(chart, [{
      x: bloque.series.map(p => p.fecha),
      y: bloque.series.map(p => p[kpiActual] ?? 0),
      type: 'scatter',
      mode: 'lines+markers',
      name: pasilloActual
    }], {
      title: `Tendencia · ${pasilloActual}`
    }, { responsive: true });
    
    console.log('✅ Gráfico creado exitosamente');
  } catch (error) {
    console.error('❌ Error al crear gráfico Plotly:', error);
  }
}

function renderComparacion(container) {
  console.log('📊 renderComparacion()');
  
  const traces = PASILLOS_VALIDOS
    .filter(p => dataPorPasillo[p])
    .map(p => ({
      x: dataPorPasillo[p].series.map(pt => pt.fecha),
      y: dataPorPasillo[p].series.map(pt => pt[kpiActual] ?? 0),
      type: 'scatter',
      mode: 'lines+markers',
      name: p
    }));

  console.log(`📊 Traces generados: ${traces.length} pasillos`);
  console.log('📊 Traces detalles:', traces.map(t => t.name));

  if (!traces.length) {
    console.error('❌ No hay traces para comparar');
    return;
  }

  const chart = document.createElement('div');
  chart.className = 'plotly-chart';
  container.appendChild(chart);

  try {
    Plotly.newPlot(chart, traces, {
      title: `Comparación · ${kpiActual.toUpperCase()}`,
      legend: { orientation: 'h' }
    }, { responsive: true });
    
    console.log('✅ Gráfico de comparación creado');
  } catch (error) {
    console.error('❌ Error al crear gráfico de comparación:', error);
  }
}

function renderTodos(container) {
  console.log('📊 renderTodos()');
  
  const grid = document.createElement('div');
  grid.className = 'pasillos-grid';

  console.log('📊 Pasillos a renderizar:', PASILLOS_VALIDOS.filter(p => dataPorPasillo[p]));

  PASILLOS_VALIDOS.forEach(p => {
    const bloque = dataPorPasillo[p];
    if (!bloque) {
      console.log(`📊 Pasillo ${p} - sin datos, omitiendo`);
      return;
    }

    console.log(`📊 Renderizando pasillo ${p}...`);
    
    const card = document.createElement('fieldset');
    card.innerHTML = `<legend>${p}</legend>`;

    const chart = document.createElement('div');
    chart.className = 'plotly-chart';
    card.appendChild(chart);

    try {
      Plotly.newPlot(chart, [{
        x: bloque.series.map(pt => pt.fecha),
        y: bloque.series.map(pt => pt[kpiActual] ?? 0),
        type: 'scatter',
        mode: 'lines+markers'
      }], {
        title: `Tendencia · ${p}`
      }, { responsive: true });
      
      console.log(`✅ Gráfico para ${p} creado`);
    } catch (error) {
      console.error(`❌ Error al crear gráfico para ${p}:`, error);
    }

    grid.appendChild(card);
  });

  container.appendChild(grid);
  console.log('✅ Todos los pasillos renderizados');
}

/* ======================================================
   HELPERS
====================================================== */
function limpiarPlotly(root) {
  if (typeof Plotly === 'undefined' || !root) {
    console.log('⚠️ limpiarPlotly: Plotly no disponible o root inválido');
    return;
  }
  
  const charts = root.querySelectorAll('.plotly-chart');
  console.log(`🧹 Limpiando ${charts.length} gráficos Plotly...`);
  
  charts.forEach(el => {
    try { 
      Plotly.purge(el);
      console.log('✅ Gráfico purgado');
    } catch (error) {
      console.warn('⚠️ Error al purgar gráfico:', error);
    }
  });
}

function normalizarPasillo(p) {
  if (!p) {
    console.log('⚠️ normalizarPasillo: entrada vacía');
    return null;
  }
  
  const v = String(p).trim().toUpperCase();
  console.log(`🔄 Normalizando "${p}" -> "${v}"`);
  
  if (PASILLOS_VALIDOS.includes(v)) {
    console.log(`✅ Pasillo válido: ${v}`);
    return v;
  }
  
  if (/^[1-4]$/.test(v)) {
    const normalizado = `P${v}`;
    console.log(`✅ Pasillo normalizado: ${v} -> ${normalizado}`);
    return normalizado;
  }
  
  console.log(`❌ Pasillo inválido: ${v}`);
  return null;
}

function label(text) {
  console.log(`🏷️ Creando label: ${text}`);
  const l = document.createElement('label');
  l.textContent = text;
  l.style.margin = '0 6px';
  return l;
}

function select(values, current, onChange) {
  console.log(`🔘 Creando select con ${values.length} opciones, valor actual: ${current}`);
  const s = document.createElement('select');
  
  values.forEach(v => {
    const o = document.createElement('option');
    o.value = v;
    o.textContent = v;
    s.appendChild(o);
  });
  
  s.value = current;
  s.addEventListener('change', () => {
    console.log(`🔘 Select cambiado a: ${s.value}`);
    onChange(s.value);
  });
  
  return s;
}

/* ======================================================
   FUNCIÓN DE DIAGNÓSTICO MANUAL
====================================================== */
window.diagnosticarPasillos = function() {
  console.log('🔬 DIAGNÓSTICO MANUAL DE PASILLOS ======================');
  console.log('🔬 1. Estado interno:');
  console.log('🔬    ultimoResultado:', ultimoResultado);
  console.log('🔬    dataPorPasillo:', dataPorPasillo);
  console.log('🔬    modoActual:', modoActual);
  console.log('🔬    pasilloActual:', pasilloActual);
  console.log('🔬    kpiActual:', kpiActual);
  
  console.log('🔬 2. DOM actual:');
  console.log('🔬    tab-pasillos:', document.getElementById('tab-pasillos'));
  console.log('🔬    tab-pasillos innerHTML (primeros 300 chars):', 
    document.getElementById('tab-pasillos')?.innerHTML?.substring(0, 300) || 'NO EXISTE');
  
  console.log('🔬 3. Todos los elementos con id que contienen "pasillos":');
  document.querySelectorAll('[id*="pasillos"]').forEach(el => {
    console.log(`🔬    - ${el.id}:`, el);
  });
  
  console.log('🔬 4. Si hay datos, intentar renderizar manualmente...');
  if (ultimoResultado) {
    console.log('🔬    Hay datos, llamando a renderSeguro()...');
    renderSeguro();
  } else {
    console.log('🔬    No hay datos aún.');
  }
  
  console.log('🔬 DIAGNÓSTICO COMPLETADO =========================');
};

console.log('✅ PasillosView listo - usa window.diagnosticarPasillos() para diagnóstico manual');