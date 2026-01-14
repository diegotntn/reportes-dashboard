/* ======================================================
   Personas State
   ======================================================
   - Estado interno encapsulado
   - Acceso SOLO mediante getters/setters
   - Persona identificada SIEMPRE por ID
====================================================== */

/* ─────────────────────────────
   CONSTANTES
───────────────────────────── */
export const MODOS = ['Individual', 'Comparación', 'Todos separados'];

export const COLORES = ['#2563eb', '#059669', '#d97706', '#dc2626'];
export const COLORES_BG = [
  'rgba(37,99,235,.15)',
  'rgba(5,150,105,.15)',
  'rgba(217,119,6,.15)',
  'rgba(220,38,38,.15)'
];

/* ─────────────────────────────
   ESTADO INTERNO (PRIVADO)
───────────────────────────── */
let dataPorPersona = {};          // { [personaId]: { nombre, serie, ... } }
let personasDisponibles = [];     // [personaId]

let modoActual = MODOS[0];
let personaActual = null;         // personaId
let kpiActual = 'importe';

// 🔑 NUEVO: periodo actual para Personas
let periodoActual = 'mes';        // 'dia' | 'semana' | 'mes'

let ultimoResultado = null;

/* ─────────────────────────────
   GETTERS (LECTURA)
───────────────────────────── */
export const getDataPorPersona = () => dataPorPersona;
export const getPersonasDisponibles = () => personasDisponibles;

export const getModoActual = () => modoActual;
export const getPersonaActual = () => personaActual;
export const getKpiActual = () => kpiActual;

// 🔑 NUEVO
export const getPeriodoActual = () => periodoActual;

export const getUltimoResultado = () => ultimoResultado;

/* ─────────────────────────────
   SETTERS (CONTROLADOS)
───────────────────────────── */
export const setModoActual = v => {
  modoActual = v;
};

export const setPersonaActual = personaId => {
  personaActual = personaId;
  console.log('[STATE Persona] personaActual ->', personaActual);
};

export const setKpiActual = kpi => {
  kpiActual = kpi;
};

// 🔑 NUEVO
export const setPeriodoActual = periodo => {
  periodoActual = periodo;
  console.log('[STATE Persona] periodoActual ->', periodoActual);
};

export const setUltimoResultado = v => {
  ultimoResultado = v;
};

/* ─────────────────────────────
   MUTADORES DE DATOS
───────────────────────────── */
export function resetPersonas() {
  dataPorPersona = {};
  personasDisponibles = [];
  personaActual = null;
  periodoActual = 'mes';
}

export function setPersonasData({ data, personas }) {
  dataPorPersona = data;
  personasDisponibles = personas;

  // 🔑 Garantiza que personaActual siempre sea un ID válido
  if (!personaActual || !dataPorPersona[personaActual]) {
    personaActual = personasDisponibles[0] ?? null;
  }
}
