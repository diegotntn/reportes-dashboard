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
  if (!TABS.includes(tab)) return;

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

  /* ───────── Buscar contenedor activo ───────── */
  const contenedor = document.getElementById(`tab-${tab}`);
  if (!contenedor) return;

  /* ───────── Montar vista HTML base ───────── */
  await montarVista(tab, contenedor);

  /* ───────── Mostrar vista activa ───────── */
  contenedor.classList.add('active');
  contenedor.style.display = 'block';

  /* ───────── Marcar tab activa (UI) ───────── */
  marcarTabActiva(tab);

  /* ───────── Emitir evento de activación ───────── */
  window.dispatchEvent(
    new CustomEvent('reportes:tab-activada', {
      detail: { tab, yaActiva }
    })
  );
}

/* ─────────────────────────────
   Montaje de vistas HTML
───────────────────────────── */

async function montarVista(tab, contenedor) {
  if (!contenedor) return;

  /* ───────── Ya montada ───────── */
  if (contenedor.dataset.montada === 'true') {
    emitirVistaMontada(tab);
    return;
  }

  /* ───────── Cache ───────── */
  if (viewCache[tab]) {
    contenedor.innerHTML = viewCache[tab];
    contenedor.dataset.montada = 'true';
    emitirVistaMontada(tab);
    return;
  }

  /* ───────── Fetch HTML ───────── */
  try {
    const ruta = `/views/reportes_${tab}.html`;
    const res = await fetch(ruta);

    if (!res.ok) throw new Error();

    const html = await res.text();

    viewCache[tab] = html;
    contenedor.innerHTML = html;
    contenedor.dataset.montada = 'true';

    emitirVistaMontada(tab);

  } catch {
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
  if (!botones.length) return;

  botones.forEach(btn => {
    btn.addEventListener('click', () => {
      activarTab(btn.dataset.tab);
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
