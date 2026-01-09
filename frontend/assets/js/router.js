/**
 * Router SPA simple
 * -----------------
 * RESPONSABILIDADES:
 * - Cargar vistas HTML
 * - Ejecutar el módulo JS asociado
 * - Controlar navegación principal
 * - Controlar visibilidad de subpestañas (Reportes)
 */

// ─────────────────────────
// Importación de módulos
// ─────────────────────────
import { cargarProductos } from './modules/productos.js';
import { cargarDevoluciones } from './modules/devoluciones/index.js';
import { cargarPersonal } from './modules/personal.js';
import { cargarReportes } from './modules/reportes/index.js';


// ─────────────────────────
// Definición de rutas principales
// ─────────────────────────
const routes = {
  productos: {
    view: 'views/productos.html',
    action: cargarProductos,
    title: 'Productos'
  },
  devoluciones: {
    view: 'views/devoluciones.html',
    action: cargarDevoluciones,
    title: 'Devoluciones'
  },
  personal: {
    view: 'views/personal.html',
    action: cargarPersonal,
    title: 'Personal'
  },
  reportes: {
    view: 'views/reportes.html',
    action: cargarReportes,
    title: 'Reportes'
  }
};


// ─────────────────────────
// SUBPESTAÑAS DE REPORTES
// ─────────────────────────
const REPORTES_TABS = ['general', 'pasillos', 'personas', 'zonas', 'detalle'];

/**
 * Muestra solo la subpestaña activa de Reportes
 */
export function mostrarTabReporte(tabActiva) {
  REPORTES_TABS.forEach(tab => {
    const el = document.getElementById(`tab-${tab}`);
    if (!el) return;
    el.style.display = (tab === tabActiva) ? 'block' : 'none';
  });
}

/**
 * Marca visualmente la pestaña activa (opcional)
 */
export function marcarTabReporte(tabActiva) {
  document.querySelectorAll('[data-tab]').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabActiva);
  });
}


// ─────────────────────────
// Navegación principal
// ─────────────────────────
export async function navegar(ruta) {
  const route = routes[ruta];

  if (!route) {
    console.error(`Ruta no encontrada: ${ruta}`);
    return;
  }

  try {
    const response = await fetch(route.view);
    if (!response.ok) {
      throw new Error(`No se pudo cargar la vista: ${route.view}`);
    }

    const html = await response.text();

    const container = document.getElementById('main-content');
    if (!container) {
      throw new Error('Contenedor #main-content no encontrado');
    }

    container.innerHTML = html;

    // Ejecutar módulo asociado
    if (typeof route.action === 'function') {
      route.action();
    }

    // Título del documento
    if (route.title) {
      document.title = `Reporte Surtido · ${route.title}`;
    }

    window.history.pushState({ ruta }, '', `#${ruta}`);

  } catch (error) {
    console.error(error);
    mostrarErrorVista();
  }
}


// ─────────────────────────
// Manejo de back / forward
// ─────────────────────────
window.addEventListener('popstate', (event) => {
  const ruta = event.state?.ruta || 'reportes';
  navegar(ruta);
});


// ─────────────────────────
// Arranque inicial
// ─────────────────────────
export function iniciarRouter() {
  const hash = window.location.hash.replace('#', '');
  const rutaInicial = hash || 'reportes'; // 👈 Arranca en Reportes
  navegar(rutaInicial);
}


// ─────────────────────────
// Vista de error genérica
// ─────────────────────────
function mostrarErrorVista() {
  const container = document.getElementById('main-content');
  if (!container) return;

  container.innerHTML = `
    <section class="error-view">
      <h2>Error</h2>
      <p>No se pudo cargar la vista solicitada.</p>
    </section>
  `;
}


// ─────────────────────────
// Exponer navegación global (navbar)
// ─────────────────────────
window.navegar = navegar;
