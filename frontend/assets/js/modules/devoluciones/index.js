// assets/js/modules/devoluciones/index.js

import { cargarHistorial } from './historial.js';
import { cargarRegistro } from './registro.js';
import { cargarEdicion } from './edicion.js';

/**
 * Módulo orquestador de DEVOLUCIONES
 *
 * RESPONSABILIDAD:
 * - Decidir qué subpantalla mostrar
 * - Escuchar eventos de navegación interna
 *
 * NO:
 * - Lógica de negocio
 * - Acceso a API
 * - Manipulación de estado
 */

export function cargarDevoluciones() {
  _bindNavigation();
  _bindEditEvent();

  // Vista por defecto
  _mostrarHistorial();
}

// ─────────────────────────────────────────────
// Navegación interna (tabs / botones)
// ─────────────────────────────────────────────
function _bindNavigation() {
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-dev]');
    if (!btn) return;

    const vista = btn.dataset.dev;

    switch (vista) {
      case 'historial':
        _mostrarHistorial();
        break;

      case 'registro':
        cargarRegistro();
        break;

      default:
        console.warn(`Vista DEVOLUCIONES no soportada: ${vista}`);
    }
  });
}

// ─────────────────────────────────────────────
// Evento semántico de edición (desde historial)
// ─────────────────────────────────────────────
function _bindEditEvent() {
  document.addEventListener('devolucion:edit', (e) => {
    const { id } = e.detail || {};
    if (!id) return;

    cargarEdicion(id);
  });
}

// ─────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────
function _mostrarHistorial() {
  _setActiveTab('historial');
  cargarHistorial();
}

function _setActiveTab(vista) {
  document.querySelectorAll('[data-dev]').forEach(btn => {
    btn.classList.toggle('is-active', btn.dataset.dev === vista);
  });
}
