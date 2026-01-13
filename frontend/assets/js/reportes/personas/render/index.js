import { getModoActual } from '../statePersona.js';
import { renderizarIndividual } from './individual.js';
import { renderizarComparacion } from './comparacion.js';
import { renderizarTodos } from './todos.js';

export function renderizarSegunModo(container) {
  switch (getModoActual()) {
    case 'Individual': return renderizarIndividual(container);
    case 'Comparación': return renderizarComparacion(container);
    case 'Todos separados': return renderizarTodos(container);
  }
}
