/**
 * PersonasView – Render central seguro
 * ===================================
 * - Punto ÚNICO de render
 * - El adapter se ejecuta SOLO cuando llega data nueva
 * - El render es puro (no reinicia estado válido)
 */

import { registrarEventosPersonas } from './events.js';
import { adaptarDatosPersonas } from './adapter.js';
import { renderizarSegunModo } from './render/index.js';
import { renderizarControles } from './controls.js';
import { estadoVacio } from './empty.js';

import {
  getModoActual,
  getKpiActual,
  getUltimoResultado,
  getPersonasDisponibles,
  getPersonaActual,
  setPersonaActual,
  setKpiActual
} from './statePersona.js';

/* ─────────────────────────────
   Render seguro (ENTRY POINT)
───────────────────────────── */
export function intentarRender() {
  const resultado = getUltimoResultado();
  if (!resultado) return;

  const tab = document.getElementById('tab-personas');
  if (!tab) return;

  const container = tab.querySelector('#personas-container');
  const controls = tab.querySelector('.personas-controls');

  if (!container) return;

  renderizar(container, controls);
}

/* ─────────────────────────────
   Render principal (PURO)
───────────────────────────── */
function renderizar(container, controls) {
  const personas = getPersonasDisponibles();

  // 1️⃣ Limpiar contenedor visual
  container.innerHTML = '';

  // 2️⃣ Estado vacío
  if (!personas.length) {
    container.innerHTML = estadoVacio(
      'No hay datos disponibles para el rango seleccionado.'
    );
    return;
  }

  // 3️⃣ Garantizar defaults SOLO si faltan
  if (!getPersonaActual() || !personas.includes(getPersonaActual())) {
    setPersonaActual(personas[0]);
  }

  if (!getKpiActual()) {
    setKpiActual('importe');
  }

  // 4️⃣ Renderizar controles (reflejan estado)
  if (controls) {
    renderizarControles(controls);
  }

  // 5️⃣ Renderizar gráfica según modo
  renderizarSegunModo(container);
}

/* ─────────────────────────────
   API pública para cargar data
   (SE USA DESDE FETCH / FILTROS)
───────────────────────────── */
export function cargarResultadoPersonas(resultado) {
  adaptarDatosPersonas(resultado); // 👈 SOLO AQUÍ se toca data
  intentarRender();
}

/* ─────────────────────────────
   DEBUG CONTROLADO KPI = 0
   (se usa desde adapter / render)
───────────────────────────── */
export function debugKpiCero({
  persona,
  kpi,
  row,
  valor
}) {
  if (valor !== 0) return;

  if (!(kpi in row)) {
    console.warn('[Personas KPI NO EXISTE]', {
      persona,
      kpi,
      clavesDisponibles: Object.keys(row),
      row
    });
    return;
  }

  if (row[kpi] == null) {
    console.warn('[Personas KPI NULL/UNDEFINED]', {
      persona,
      kpi,
      valorOriginal: row[kpi],
      row
    });
  }
}

/* ─────────────────────────────
   Init del módulo
───────────────────────────── */
registrarEventosPersonas();
