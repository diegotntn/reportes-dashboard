/**
 * Estado global de la aplicación
 * --------------------------------
 * REGLAS:
 * - SOLO almacena datos
 * - NO hace fetch
 * - NO valida
 * - NO formatea
 * - NO contiene lógica de negocio
 */

/**
 * Estado reactivo simple (plain object)
 */
export const state = {
  // ─────────────────────────
  // Datos principales
  // ─────────────────────────
  productos: [],
  devoluciones: [],
  personal: [],
  vendedores: [],

  // ─────────────────────────
  // Reportes
  // ─────────────────────────
  reportes: {
    tabla: [],
    graficas: {},
    resumen: {}
  },

  // ─────────────────────────
  // Filtros activos
  // ─────────────────────────
  filtros: {
    fecha_desde: null,
    fecha_hasta: null,
    producto_id: null,
    vendedor_id: null,
    zona: null
  },

  // ─────────────────────────
  // UI (estado visual, no lógica)
  // ─────────────────────────
  ui: {
    cargando: false,
    vistaActual: null,
    error: null
  }
};

/**
 * Reset parcial o total del estado
 * (útil al cambiar de módulo o cerrar sesión)
 */
export function resetState(seccion = null) {
  if (!seccion) {
    state.productos = [];
    state.devoluciones = [];
    state.personal = [];
    state.vendedores = [];
    state.reportes = { tabla: [], graficas: {}, resumen: {} };
    state.filtros = {
      fecha_desde: null,
      fecha_hasta: null,
      producto_id: null,
      vendedor_id: null,
      zona: null
    };
    state.ui = { cargando: false, vistaActual: null, error: null };
    return;
  }

  if (state[seccion] !== undefined) {
    if (Array.isArray(state[seccion])) state[seccion] = [];
    else if (typeof state[seccion] === 'object') state[seccion] = {};
  }
}
