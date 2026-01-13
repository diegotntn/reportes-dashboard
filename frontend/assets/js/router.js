/**
 * Router interno de Reportes
 * =========================
 *
 * RESPONSABILIDADES:
 * - Controlar subpestañas de reportes
 * - Montar la vista HTML correspondiente (una sola vez)
 * - Activar / desactivar paneles vía CSS
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

/* ─────────────────────────────
   API pública
───────────────────────────── */

export async function iniciarTabsReportes(tabInicial = 'general') {
  registrarEventosTabs();
  await activarTab(tabInicial);
}

export async function activarTab(tab) {
  console.group(`[Tabs] activarTab → ${tab}`);

  /* ───────── Validación ───────── */
  if (!TABS.includes(tab)) {
    console.warn('[Tabs] ❌ Tab no válida:', tab);
    console.groupEnd();
    return;
  }

  const yaActiva = tab === tabActiva;
  console.log('[Tabs] ¿Ya estaba activa?', yaActiva);

  tabActiva = tab;
  console.log('[Tabs] tabActiva =', tabActiva);

  /* ───────── Ocultar todas las vistas ───────── */
  console.log('[Tabs] Ocultando vistas...');
  TABS.forEach(t => {
    const el = document.getElementById(`tab-${t}`);
    if (el) {
      el.classList.remove('active');
      el.style.display = 'none';
      console.log(`   ⤵ ocultada: #tab-${t}`);
    } else {
      console.warn(`   ⚠ no existe: #tab-${t}`);
    }
  });

  /* ───────── Buscar contenedor activo ───────── */
  const contenedor = document.getElementById(`tab-${tab}`);
  if (!contenedor) {
    console.error(`[Tabs] ❌ Contenedor #tab-${tab} no encontrado`);
    console.groupEnd();
    return;
  }

  console.log('[Tabs] Contenedor encontrado:', contenedor);

  /* ───────── Montar vista HTML base ───────── */
  console.log('[Tabs] Montando vista:', tab);
  await montarVista(tab, contenedor);
  console.log('[Tabs] Vista montada:', tab);

  /* ───────── Mostrar vista activa ───────── */
  contenedor.classList.add('active');
  contenedor.style.display = 'block';
  console.log('[Tabs] Vista visible:', tab);

  /* ───────── Marcar tab activa (UI) ───────── */
  marcarTabActiva(tab);
  console.log('[Tabs] Tab marcada como activa en UI');

  /* ───────── Emitir evento de activación ───────── */
  console.log('[Tabs] Emitiendo evento reportes:tab-activada');
  window.dispatchEvent(
    new CustomEvent('reportes:tab-activada', {
      detail: { tab, yaActiva }
    })
  );

  console.groupEnd();
}


/* ─────────────────────────────
   Montaje de vistas HTML
───────────────────────────── */

async function montarVista(tab, contenedor) {
  console.group(`[Vista] montarVista → ${tab}`);

  if (!contenedor) {
    console.error('[Vista] ❌ contenedor no recibido');
    console.groupEnd();
    return;
  }

  /* ───────── Ya montada ───────── */
  if (contenedor.dataset.montada === 'true') {
    console.log('[Vista] Ya montada, solo emite evento');
    emitirVistaMontada(tab);
    console.groupEnd();
    return;
  }

  /* ───────── Cache ───────── */
  if (viewCache[tab]) {
    console.log('[Vista] Usando cache para:', tab);

    contenedor.innerHTML = viewCache[tab];
    contenedor.dataset.montada = 'true';

    console.log('[Vista] HTML inyectado desde cache');
    emitirVistaMontada(tab);

    console.groupEnd();
    return;
  }

  /* ───────── Fetch HTML ───────── */
  try {
    const ruta = `/views/reportes_${tab}.html`;
    console.log('[Vista] Fetch:', ruta);

    const res = await fetch(ruta);

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const html = await res.text();
    console.log('[Vista] HTML recibido (length):', html.length);

    // Cachear ANTES de montar
    viewCache[tab] = html;

    // Montar HTML
    contenedor.innerHTML = html;
    contenedor.dataset.montada = 'true';

    // 🔎 Verificación crítica
    const tieneContenido = contenedor.children.length > 0;
    console.log('[Vista] Contenido montado:', tieneContenido);

    emitirVistaMontada(tab);

  } catch (err) {
    console.error(`[Vista] ❌ Error cargando vista "${tab}"`, err);

    contenedor.innerHTML = `
      <section class="card error">
        <h3>Error cargando vista</h3>
        <p>No se pudo cargar <strong>${tab}</strong>.</p>
      </section>
    `;

    contenedor.dataset.montada = 'true';
    emitirVistaMontada(tab);
  }

  console.groupEnd();
}

/* ─────────────────────────────
   Eventos de ciclo de vida
───────────────────────────── */

function emitirVistaMontada(tab) {
  // Garantiza que el HTML ya esté en el DOM
  requestAnimationFrame(() => {
    window.dispatchEvent(
      new CustomEvent('reportes:vista-montada', {
        detail: {
          tab,
          contenedor: document.getElementById(`tab-${tab}`)
        }
      })
    );
  });
}

/* ─────────────────────────────
   UI Tabs
───────────────────────────── */

function registrarEventosTabs() {
  console.log('[Tabs] Registrando eventos de tabs...');

  const botones = document.querySelectorAll('[data-tab]');
  console.log('[Tabs] Botones encontrados:', botones.length);

  if (!botones.length) {
    console.warn('[Tabs] ❌ No se encontraron botones data-tab');
    return;
  }

  botones.forEach(btn => {
    console.log('[Tabs] Botón detectado:', btn.dataset.tab);

    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;

      console.log('👉 [Tabs] Click en tab:', tab);
      console.log('👉 [Tabs] Elemento:', btn);

      activarTab(tab);
    });
  });
}

function marcarTabActiva(tab) {
  document.querySelectorAll('[data-tab]').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tab);
  });
}

/* ─────────────────────────────
   Utilidades
───────────────────────────── */

export function forzarRecargaVista(tab) {
  delete viewCache[tab];
  const contenedor = document.getElementById(`tab-${tab}`);
  if (contenedor) {
    delete contenedor.dataset.montada;
  }
}
