/**
 * Historial de Devoluciones
 * -------------------------
 * Equivalente a HistorialView (Tkinter)
 *
 * RESPONSABILIDADES:
 * - Inicializar eventos
 * - Cargar historial desde API
 * - Renderizar tabla
 *
 * NO:
 * - Cargar vistas HTML principales (eso lo hace el router)
 */

import { obtenerDevoluciones } from '../../api.js';
import { state } from '../../state.js';


// ─────────────────────────────
// ENTRY POINT (lo llama el módulo index.js)
// ─────────────────────────────
export async function cargarHistorial() {
  _bindActions();
  await _cargarHistorial();
}


// ─────────────────────────────
// Carga de datos (API)
// ─────────────────────────────
async function _cargarHistorial() {
  _setLoading(true);
  _clearError();

  try {
    const data = await obtenerDevoluciones();

    // Normalizar
    state.devoluciones = Array.isArray(data) ? data : [];

    _renderTabla(state.devoluciones);

  } catch (error) {
    console.error('❌ Error al cargar historial', error);
    _setError('No se pudo cargar el historial de devoluciones');

  } finally {
    _setLoading(false);
  }
}


// ─────────────────────────────
// Acciones UI
// ─────────────────────────────
function _bindActions() {
  const btnRefresh = document.getElementById('btn-refresh');

  btnRefresh?.addEventListener('click', _cargarHistorial);

  // Delegación para botones dinámicos
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-edit-id]');
    if (!btn) return;

    document.dispatchEvent(
      new CustomEvent('devolucion:edit', {
        detail: { id: btn.dataset.editId }
      })
    );
  });
}


// ─────────────────────────────
// Render tabla
// ─────────────────────────────
function _renderTabla(rows = []) {
  const tbody = document.querySelector('#table tbody');
  const empty = document.getElementById('historial-empty');

  if (!tbody) {
    console.warn('⚠️ Tabla no encontrada (#table tbody)');
    return;
  }

  tbody.innerHTML = '';

  if (!rows.length) {
    if (empty) empty.hidden = false;
    return;
  }

  if (empty) empty.hidden = true;

  rows.forEach(row => {
    const tr = document.createElement('tr');

    tr.innerHTML = `
      <td>${row.fecha ?? ''}</td>
      <td>${row.producto ?? ''}</td>
      <td>${row.cantidad ?? ''}</td>
      <td>${row.motivo ?? ''}</td>
      <td>
        <button
          class="btn btn--small"
          data-edit-id="${row.id}"
        >
          Editar
        </button>
      </td>
    `;

    tbody.appendChild(tr);
  });
}


// ─────────────────────────────
// Estados UI
// ─────────────────────────────
function _setLoading(isLoading) {
  const el = document.getElementById('historial-loading');
  if (el) el.hidden = !isLoading;
}

function _setError(message) {
  const el = document.getElementById('historial-error');
  if (!el) return;

  el.textContent = message;
  el.hidden = false;
}

function _clearError() {
  const el = document.getElementById('historial-error');
  if (el) el.hidden = true;
}
