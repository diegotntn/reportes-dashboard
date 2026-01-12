/**
 * Router interno de Reportes - VERSIÓN CON DIAGNÓSTICO
 * ==========================
 *
 * RESPONSABILIDADES:
 * - Controlar subpestañas de reportes
 * - Montar la vista HTML correspondiente (una sola vez)
 * - Activar / desactivar paneles vía CLASES CSS
 * - Marcar la pestaña activa
 * - Emitir eventos de navegación y montaje
 *
 * NO HACE:
 * - Fetch de datos
 * - Lógica de negocio
 * - Render de gráficas
 */

const TABS = ['general', 'pasillos', 'personas', 'zonas', 'detalle'];
const viewCache = {};

let tabActiva = null;
let diagnosticoRouter = true; // Cambiar a false cuando se resuelva

/* ─────────────────────────────
   API pública
───────────────────────────── */

export async function iniciarTabsReportes(tabInicial = 'general') {
  console.log('🚀 [Router] iniciarTabsReportes()');
  console.log('🚀 Tab inicial:', tabInicial);
  
  if (diagnosticoRouter) {
    console.log('🔍 DIAGNÓSTICO ROUTER - INICIO ======================');
    console.log('🔍 1. Verificando estructura DOM inicial...');
    console.log('🔍 Contenedores tab-* en el DOM:');
    TABS.forEach(t => {
      const el = document.getElementById(`tab-${t}`);
      console.log(`   - tab-${t}:`, el ? `EXISTE (display: ${el.style.display})` : 'NO EXISTE');
    });
    
    console.log('🔍 2. Botones data-tab encontrados:');
    document.querySelectorAll('[data-tab]').forEach(btn => {
      console.log(`   - ${btn.dataset.tab}:`, btn);
    });
  }
  
  registrarEventosTabs();
  await activarTab(tabInicial);
}

export async function activarTab(tab) {
  console.groupCollapsed(`🧭 [Router] activarTab("${tab}")`);
  console.time(`activarTab-${tab}`);

  console.log('📌 Tab solicitada:', tab);
  console.log('📌 Tab activa anterior:', tabActiva);

  if (!TABS.includes(tab)) {
    console.error('[Router] ❌ Tab no válida:', tab);
    console.groupEnd();
    console.timeEnd(`activarTab-${tab}`);
    return;
  }

  const yaActiva = tab === tabActiva;
  console.log('📌 ¿Ya estaba activa?:', yaActiva);
  tabActiva = tab;

  if (diagnosticoRouter) {
    console.log('🔍 DIAGNÓSTICO: Ocultando todas las vistas...');
  }

  /* ───────── Ocultar todas las vistas ───────── */
  TABS.forEach(t => {
    const el = document.getElementById(`tab-${t}`);
    if (el) {
      const estabaActivo = el.classList.contains('active');
      el.classList.remove('active');
      el.style.display = 'none';
      
      if (diagnosticoRouter && estabaActivo) {
        console.log(`🔍   tab-${t} estaba activo, ahora oculto`);
      }
    } else if (diagnosticoRouter) {
      console.log(`⚠️   tab-${t} no existe en el DOM`);
    }
  });

  const contenedor = document.getElementById(`tab-${tab}`);
  console.log('📌 Contenedor encontrado:', contenedor);
  
  if (!contenedor) {
    console.error(`[Router] ❌ CRÍTICO: Contenedor #tab-${tab} no encontrado`);
    console.error(`[Router] Revisa que en tu HTML exista: <div id="tab-${tab}"></div>`);
    
    // Mostrar todos los IDs en la página
    console.error('[Router] IDs existentes en la página:');
    document.querySelectorAll('[id]').forEach(el => {
      if (el.id.includes('tab')) {
        console.error(`   - ${el.id}`);
      }
    });
    
    console.groupEnd();
    console.timeEnd(`activarTab-${tab}`);
    return;
  }

  /* ───────── Montar vista (HTML garantizado) ───────── */
  console.log('📌 Iniciando montaje de vista...');
  await montarVista(tab, contenedor);

  /* ───────── Mostrar vista activa ───────── */
  contenedor.classList.add('active');
  contenedor.style.display = 'block';
  
  if (diagnosticoRouter) {
    console.log(`🔍 tab-${tab} ahora: display=${contenedor.style.display}, class=${contenedor.className}`);
    console.log(`🔍 InnerHTML después del montaje (primeros 300 chars):`);
    console.log(contenedor.innerHTML.substring(0, 300));
    console.log(`🔍 Longitud del HTML:`, contenedor.innerHTML.length);
  }
  
  marcarTabActiva(tab);

  /* ───────── Emitir evento de navegación ───────── */
  if (yaActiva) {
    console.log('🔄 Tab ya activa → re-emitiendo evento');
  } else {
    console.log('➡️ Tab nueva → emitiendo evento');
  }

  window.dispatchEvent(
    new CustomEvent('reportes:tab-activada', {
      detail: { tab }
    })
  );

  console.groupEnd();
  console.timeEnd(`activarTab-${tab}`);
}

/* ─────────────────────────────
   Montaje de vistas (HTML REAL) - CON DIAGNÓSTICO
───────────────────────────── */

async function montarVista(tab, contenedor) {
  console.groupCollapsed(`📂 [Router] montarVista("${tab}")`);
  console.time(`montarVista-${tab}`);
  
  console.log('📂 Contenedor recibido:', contenedor);
  console.log('📂 contenedor.dataset.montada:', contenedor.dataset.montada);
  console.log('📂 ¿viewCache[tab] existe?:', viewCache[tab] ? 'SÍ' : 'NO');

  // Ya montada
  if (contenedor.dataset.montada === 'true') {
    console.log('📂 Vista ya estaba montada, emitiendo evento...');
    emitirVistaMontada(tab);
    console.groupEnd();
    console.timeEnd(`montarVista-${tab}`);
    return;
  }

  // En cache
  if (viewCache[tab]) {
    console.log('📂 Usando HTML desde caché...');
    console.log('📂 Longitud del HTML en caché:', viewCache[tab].length);
    console.log('📂 HTML caché (primeros 200 chars):', viewCache[tab].substring(0, 200));
    
    contenedor.innerHTML = viewCache[tab];
    contenedor.dataset.montada = 'true';
    
    console.log('📂 HTML inyectado desde caché');
    console.log('📂 contenedor.dataset.montada ahora:', contenedor.dataset.montada);
    
    emitirVistaMontada(tab);
    console.groupEnd();
    console.timeEnd(`montarVista-${tab}`);
    return;
  }

  // Cargar desde archivo
  try {
    const ruta = `/views/reportes_${tab}.html`;
    console.log('📂 Cargando desde ruta:', ruta);
    console.time(`fetch-${tab}`);
    
    const res = await fetch(ruta);
    console.timeEnd(`fetch-${tab}`);
    
    console.log('📂 Response status:', res.status);
    console.log('📂 Response ok:', res.ok);
    console.log('📂 Response headers:', Object.fromEntries([...res.headers.entries()]));

    if (!res.ok) {
      console.error(`📂 Error HTTP ${res.status} al cargar ${ruta}`);
      console.error('📂 URL completa:', new URL(ruta, window.location.origin).href);
      throw new Error(`HTTP ${res.status}`);
    }

    console.time(`text-${tab}`);
    const html = await res.text();
    console.timeEnd(`text-${tab}`);
    
    console.log('📂 HTML obtenido correctamente');
    console.log('📂 Longitud del HTML:', html.length);
    console.log('📂 Primeros 500 caracteres del HTML:');
    console.log(html.substring(0, 500));
    console.log('📂 ¿HTML está vacío?:', html.trim().length === 0);
    
    // Verificar estructura mínima
    if (html.trim().length === 0) {
      console.warn('⚠️ ¡ADVERTENCIA! El HTML está vacío o solo tiene espacios en blanco');
    }
    
    if (!html.includes('<')) {
      console.warn('⚠️ ¡ADVERTENCIA! El HTML no parece contener etiquetas HTML');
    }

    viewCache[tab] = html;
    console.log('📂 HTML almacenado en caché');

    console.log('📂 Inyectando HTML en el contenedor...');
    console.log('📂 contenedor.innerHTML antes:', contenedor.innerHTML);
    
    contenedor.innerHTML = html;
    contenedor.dataset.montada = 'true';
    
    console.log('📂 contenedor.innerHTML después:', contenedor.innerHTML.substring(0, 300));
    console.log('📂 contenedor.dataset.montada ahora:', contenedor.dataset.montada);

    console.info(`[ReportesRouter] ✅ Vista '${tab}' montada exitosamente`);
    emitirVistaMontada(tab);

  } catch (err) {
    console.error(`[ReportesRouter] ❌ Error al montar vista '${tab}'`, err);
    console.error('Detalles del error:', err.message);
    console.error('Stack:', err.stack);
    
    const errorHTML = `
      <section class="card error">
        <h3>Error cargando vista</h3>
        <p>No se pudo cargar la vista <strong>${tab}</strong>.</p>
        <p><small>Error: ${err.message}</small></p>
        <p><small>Ruta intentada: /views/reportes_${tab}.html</small></p>
      </section>
    `;
    
    contenedor.innerHTML = errorHTML;
    contenedor.dataset.montada = 'true';
    
    // Aún emitimos el evento para que las vistas puedan mostrar el error
    emitirVistaMontada(tab);
  }

  console.groupEnd();
  console.timeEnd(`montarVista-${tab}`);
}

/* ─────────────────────────────
   Eventos de ciclo de vida
───────────────────────────── */

function emitirVistaMontada(tab) {
  console.log(`📨 [Router] emitirVistaMontada("${tab}")`);
  
  if (diagnosticoRouter) {
    console.log(`🔍 Emitiendo evento en requestAnimationFrame...`);
    console.log(`🔍 El HTML debería estar ya en el DOM para la pestaña ${tab}`);
  }

  // IMPORTANTE: solo cuando el HTML YA está en el DOM
  requestAnimationFrame(() => {
    console.log(`📨 [Router] Enviando evento reportes:vista-montada para "${tab}"`);
    
    window.dispatchEvent(
      new CustomEvent('reportes:vista-montada', {
        detail: { 
          tab,
          timestamp: Date.now(),
          contenedor: document.getElementById(`tab-${tab}`)
        }
      })
    );
    
    if (diagnosticoRouter) {
      console.log(`🔍 Evento enviado. Verifica que los listeners lo capturen.`);
    }
  });
}

/* ─────────────────────────────
   UI Tabs - CON DIAGNÓSTICO
───────────────────────────── */

function registrarEventosTabs() {
  console.log('🎛️ [Router] registrarEventosTabs()');
  
  const botones = document.querySelectorAll('[data-tab]');
  console.log('🎛️ Botones encontrados:', botones.length);
  
  if (botones.length === 0) {
    console.error('❌ [Router] No se encontraron botones con data-tab');
    console.error('❌ Revisa que en tu HTML existan botones como:');
    console.error('❌ <button data-tab="general">General</button>');
    return;
  }

  botones.forEach((btn, index) => {
    console.log(`🎛️ Configurando botón ${index}:`, btn);
    console.log(`🎛️   data-tab: ${btn.dataset.tab}`);
    console.log(`🎛️   texto: ${btn.textContent}`);
    
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;

      console.group('🧭 [Tabs] Click');
      console.log('🖱️ Botón clickeado:', btn);
      console.log('🖱️ data-tab:', tab);
      console.log('🖱️ ¿Es tab válida?:', TABS.includes(tab));
      console.groupEnd();

      activarTab(tab);
    });
  });
  
  console.log('✅ Eventos de tabs registrados');
}

function marcarTabActiva(tabActiva) {
  console.log(`🏷️ [Router] marcarTabActiva("${tabActiva}")`);
  
  const botones = document.querySelectorAll('[data-tab]');
  console.log(`🏷️ Actualizando ${botones.length} botones`);
  
  botones.forEach(btn => {
    const esActiva = btn.dataset.tab === tabActiva;
    const antesActiva = btn.classList.contains('active');
    
    btn.classList.toggle('active', esActiva);
    
    if (diagnosticoRouter && (esActiva || antesActiva)) {
      console.log(`🏷️   ${btn.dataset.tab}: ${antesActiva ? 'antes activa' : 'inactiva'} → ${esActiva ? 'ACTIVA' : 'inactiva'}`);
    }
  });
}

/* ─────────────────────────────
   FUNCIONES DE DIAGNÓSTICO
───────────────────────────── */

export function diagnosticarRouter() {
  console.group('🔬 DIAGNÓSTICO COMPLETO DEL ROUTER ======================');
  
  console.log('🔬 1. Estado interno:');
  console.log('🔬    tabActiva:', tabActiva);
  console.log('🔬    viewCache keys:', Object.keys(viewCache));
  console.log('🔬    viewCache sizes:');
  Object.entries(viewCache).forEach(([key, value]) => {
    console.log(`🔬      ${key}: ${value.length} chars`);
  });
  
  console.log('🔬 2. DOM actual - Contenedores:');
  TABS.forEach(t => {
    const el = document.getElementById(`tab-${t}`);
    console.log(`🔬    tab-${t}:`, el ? 'EXISTE' : 'NO EXISTE');
    if (el) {
      console.log(`🔬      display: ${el.style.display}`);
      console.log(`🔬      class: ${el.className}`);
      console.log(`🔬      dataset.montada: ${el.dataset.montada}`);
      console.log(`🔬      innerHTML length: ${el.innerHTML.length}`);
    }
  });
  
  console.log('🔬 3. Botones de navegación:');
  const botones = document.querySelectorAll('[data-tab]');
  console.log(`🔬    Total botones: ${botones.length}`);
  botones.forEach(btn => {
    console.log(`🔬      ${btn.dataset.tab}: class="${btn.className}"`);
  });
  
  console.log('🔬 4. Verificando archivos HTML:');
  TABS.forEach(async tab => {
    const ruta = `/views/reportes_${tab}.html`;
    console.log(`🔬    Probando ${ruta}...`);
    
    try {
      const res = await fetch(ruta, { method: 'HEAD' });
      console.log(`🔬      ${ruta}: ${res.ok ? '✅ EXISTE' : '❌ NO EXISTE'} (${res.status})`);
    } catch (err) {
      console.log(`🔬      ${ruta}: ❌ ERROR - ${err.message}`);
    }
  });
  
  console.log('🔬 DIAGNÓSTICO COMPLETADO =========================');
  console.groupEnd();
}

export function forzarRecargaVista(tab) {
  console.log(`🔄 [Router] Forzando recarga de vista "${tab}"`);
  
  if (viewCache[tab]) {
    console.log(`🔄 Eliminando caché para "${tab}"`);
    delete viewCache[tab];
  }
  
  const contenedor = document.getElementById(`tab-${tab}`);
  if (contenedor) {
    console.log(`🔄 Limpiando dataset.montada para "${tab}"`);
    delete contenedor.dataset.montada;
  }
  
  console.log(`🔄 Ahora activa la pestaña nuevamente para recargar`);
}

// Exponer diagnóstico globalmente
window.diagnosticarRouter = diagnosticarRouter;
window.forzarRecargaVista = forzarRecargaVista;

console.log('✅ Router cargado - use window.diagnosticarRouter() para diagnóstico');