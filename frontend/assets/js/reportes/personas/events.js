import { setUltimoResultado, getUltimoResultado } from './statePersona.js';
import { intentarRender } from './index.js';

export function registrarEventosPersonas() {

  window.addEventListener('reportes:actualizados', e => {
    setUltimoResultado(e.detail);
    intentarRender();
  });

  window.addEventListener('reportes:tab-activada', e => {
    if (e.detail?.tab === 'personas' && getUltimoResultado()) {
      intentarRender();
    }
  });
}
