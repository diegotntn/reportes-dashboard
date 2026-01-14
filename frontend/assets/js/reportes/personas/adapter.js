import { resetPersonas, setPersonasData } from './statePersona.js';

/* ======================================================
   Helpers
====================================================== */

function normalizarPeriodo(agrupar) {
  if (!agrupar) return 'mes';

  const a = agrupar.toLowerCase();
  if (a === 'dia') return 'dia';
  if (a === 'semana') return 'semana';
  if (a === 'mes') return 'mes';
  if (a === 'anio') return 'anio';

  return 'mes';
}

function toNumberSeguro(v) {
  if (v == null) return 0;
  if (typeof v === 'number') return v;

  const n = Number(String(v).replace(/[^\d.-]/g, ''));
  return Number.isFinite(n) ? n : 0;
}

function normalizarKPIs(row) {
  return {
    importe: toNumberSeguro(
      row.importe ??
      row.importe_total ??
      row.total_importe
    ),

    piezas: toNumberSeguro(
      row.piezas ??
      row.piezas_total ??
      row.total_piezas
    ),

    devoluciones: toNumberSeguro(
      row.devoluciones ??
      row.devoluciones_total ??
      row.total_devoluciones
    )
  };
}

/* ======================================================
   Adapter principal
====================================================== */

export function adaptarDatosPersonas(resultado) {
  console.group('[Personas][Adapter]');

  resetPersonas();

  const bruto = resultado?.por_persona ?? {};
  const mapaPersonas = resultado?.personas ?? {};

  const data = {};
  const personas = [];

  const periodo = normalizarPeriodo(resultado?.agrupar);

  console.log('periodo normalizado:', periodo);
  console.log('personas recibidas:', mapaPersonas);
  console.log('personas con datos:', Object.keys(bruto));

  Object.entries(bruto).forEach(([personaId, bloque]) => {
    console.group(`[Persona ${personaId}]`);

    if (!Array.isArray(bloque.tabla) || bloque.tabla.length === 0) {
      console.warn('bloque.tabla vacío o inválido');
      console.groupEnd();
      return;
    }

    const nombre = mapaPersonas[personaId] ?? personaId;

    personas.push(personaId);

    const serie = bloque.tabla.map(row => ({
      periodo: row.periodo ?? row.fecha ?? null,
      kpis: normalizarKPIs(row)
    }));

    data[personaId] = {
      id: personaId,
      nombre,
      periodo,
      serie,
      resumen: {
        ...bloque.resumen,
        nombre
      }
    };

    console.log('[DATA FINAL PERSONA]', data[personaId]);
    console.groupEnd();
  });

  console.log('[Personas][Adapter] personas finales:', personas);
  console.log('[Personas][Adapter] data final:', data);

  setPersonasData({
    data,
    personas,
    mapaPersonas   // 🔑 opcional pero útil globalmente
  });

  console.groupEnd();
}
