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
  if (!TABS.includes(tab)) {
    console.warn('[Router] Tab no válida:', tab);
    return;
  }

  const yaActiva = tab === tabActiva;
  tabActiva = tab;

  /* ───────── Ocultar todas las vistas ───────── */
  TABS.forEach(t => {
    const el = document.getElementById(`tab-${t}`);
    if (el) {
      el.classList.remove('active');
      el.style.display = 'none';
    }
  });

  const contenedor = document.getElementById(`tab-${tab}`);
  if (!contenedor) {
    console.error(`[Router] Contenedor #tab-${tab} no encontrado`);
    return;
  }

  /* ───────── Montar vista (solo HTML base) ───────── */
  await montarVista(tab, contenedor);

  /* ───────── Mostrar vista activa ───────── */
  contenedor.classList.add('active');
  contenedor.style.display = 'block';

  marcarTabActiva(tab);

  /* ───────── Emitir eventos ───────── */
  window.dispatchEvent(
    new CustomEvent('reportes:tab-activada', {
      detail: { tab, yaActiva }
    })
  );
}

/* ─────────────────────────────
   Montaje de vistas
───────────────────────────── */

async function montarVista(tab, contenedor) {

  // Ya montada
  if (contenedor.dataset.montada === 'true') {
    emitirVistaMontada(tab);
    return;
  }

  // En caché
  if (viewCache[tab]) {
    contenedor.innerHTML = viewCache[tab];
    contenedor.dataset.montada = 'true';
    emitirVistaMontada(tab);
    return;
  }

  // Cargar HTML
  try {
    const ruta = `/views/reportes_${tab}.html`;
    const res = await fetch(ruta);

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const html = await res.text();
    viewCache[tab] = html;

    contenedor.innerHTML = html;
    contenedor.dataset.montada = 'true';

    emitirVistaMontada(tab);

  } catch (err) {
    console.error(`[Router] Error cargando vista "${tab}"`, err);

    contenedor.innerHTML = `
      <section class="card error">
        <h3>Error cargando vista</h3>
        <p>No se pudo cargar <strong>${tab}</strong>.</p>
      </section>
    `;
    contenedor.dataset.montada = 'true';

    emitirVistaMontada(tab);
  }
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
  const botones = document.querySelectorAll('[data-tab]');

  if (!botones.length) {
    console.warn('[Router] No se encontraron botones data-tab');
    return;
  }

  botones.forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
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
   Utilidades opcionales
───────────────────────────── */

export function forzarRecargaVista(tab) {
  delete viewCache[tab];
  const contenedor = document.getElementById(`tab-${tab}`);
  if (contenedor) {
    delete contenedor.dataset.montada;
  }
}
