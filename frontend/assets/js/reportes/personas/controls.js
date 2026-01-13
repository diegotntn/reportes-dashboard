import {
  MODOS,
  getModoActual,
  setModoActual,
  getPersonasDisponibles,
  getPersonaActual,
  setPersonaActual,
  getKpiActual,
  setKpiActual,
  getDataPorPersona
} from './statePersona.js';

import { intentarRender } from './index.js';

/* ─────────────────────────────
   Render de controles (Modo / Persona / KPI)
───────────────────────────── */
export function renderizarControles(container) {
  if (!container) return;

  container.innerHTML = '';
  container.style.cssText = `
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 16px;
  `;

  // ───── MODO ─────
  container.appendChild(
    crearSelectorSimple(
      'Modo',
      MODOS.map(m => ({ value: m, label: m })),
      getModoActual(),
      valor => {
        setModoActual(valor);
        intentarRender();
      }
    )
  );

  // ───── PERSONA (ID → nombre visible) ─────
  const personas = getPersonasDisponibles();
  const data = getDataPorPersona();

  const opcionesPersonas = personas.map(id => ({
    value: id,
    label: data[id]?.nombre ?? id
  }));

  container.appendChild(
    crearSelectorSimple(
      'Persona',
      opcionesPersonas,
      getPersonaActual(),
      valor => {
        setPersonaActual(valor);
        intentarRender();
      }
    )
  );

  // ───── KPI ─────
  container.appendChild(
    crearSelectorSimple(
      'KPI',
      [
        { value: 'importe', label: 'Importe' },
        { value: 'piezas', label: 'Piezas' },
        { value: 'devoluciones', label: 'Devoluciones' }
      ],
      getKpiActual(),
      valor => {
        setKpiActual(valor);
        intentarRender();
      }
    )
  );
}

/* ─────────────────────────────
   Helper: selector reutilizable (value / label)
───────────────────────────── */
function crearSelectorSimple(labelText, opciones, valorActual, onChange) {
  const wrapper = document.createElement('div');
  wrapper.style.cssText = `
    display: flex;
    align-items: center;
    gap: 6px;
  `;

  const label = document.createElement('span');
  label.textContent = `${labelText}:`;
  label.style.cssText = `
    font-weight: 500;
    color: #475569;
    font-size: 14px;
  `;

  const select = document.createElement('select');
  select.style.cssText = `
    padding: 6px 10px;
    border-radius: 6px;
    border: 1px solid #cbd5e1;
    background: #fff;
    font-size: 14px;
    color: #334155;
    cursor: pointer;
    min-width: 140px;
  `;

  opciones.forEach(({ value, label }) => {
    const opt = document.createElement('option');
    opt.value = value;
    opt.textContent = label;
    opt.selected = value === valorActual;
    select.appendChild(opt);
  });

  select.addEventListener('change', e => {
    onChange(e.target.value);
  });

  wrapper.appendChild(label);
  wrapper.appendChild(select);

  return wrapper;
}
