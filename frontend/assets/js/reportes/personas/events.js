import {
  setUltimoResultado,
  getUltimoResultado,
  setPeriodoActual
} from './statePersona.js';

import { intentarRender } from './index.js';

/* ======================================================
   Registro de eventos para Personas
====================================================== */

export function registrarEventosPersonas() {

  // 📥 Resultado nuevo desde backend
  window.addEventListener('reportes:actualizados', e => {
    const resultado = e.detail;
    if (!resultado) return;

    // 🔑 CLAVE: sincronizar el periodo con Personas
    // Viene del selector "Agrupar por"
    if (resultado.agrupar) {
      setPeriodoActual(resultado.agrupar); // 'dia' | 'semana' | 'mes'
    }

    // Guardar resultado completo
    setUltimoResultado(resultado);

    // Intentar render si la vista está lista
    intentarRender();
  });

  // 🧭 Activación de la pestaña Personas
  window.addEventListener('reportes:tab-activada', e => {
    if (e.detail?.tab === 'personas' && getUltimoResultado()) {
      intentarRender();
    }
  });
}
