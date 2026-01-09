/**
 * api.js
 * -------------------------------------------------
 * Capa de comunicación con el backend
 * Responsabilidad única: HTTP / Fetch
 * NO maneja DOM
 * NO maneja lógica de UI
 */

/* ───────── Configuración base ───────── */

const API_CONFIG = {
  BASE_URL: 'http://127.0.0.1:8000/api',
  TIMEOUT: 15000
};


/* ───────── Fetch con timeout ───────── */

async function fetchWithTimeout(url, options = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(
    () => controller.abort(),
    API_CONFIG.TIMEOUT
  );

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {})
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    return await response.json();

  } catch (error) {
    console.error('❌ Error API:', error.message);
    throw error;

  } finally {
    clearTimeout(timeoutId);
  }
}


/* ───────── API genérica ───────── */

export async function apiGet(path, params = {}) {
  const url = new URL(API_CONFIG.BASE_URL + path);

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') {
      url.searchParams.append(key, value);
    }
  });

  return fetchWithTimeout(url.toString(), { method: 'GET' });
}


export async function apiPost(path, data = {}) {
  return fetchWithTimeout(
    API_CONFIG.BASE_URL + path,
    {
      method: 'POST',
      body: JSON.stringify(data)
    }
  );
}


/* ───────── ENDPOINTS ESPECÍFICOS ───────── */

// 🔴 AQUÍ ESTABA EL PROBLEMA LÓGICO (NO TÉCNICO)
export async function generarReporte(filtros = {}) {

  // 🔎 LOG ÚNICO Y CLARO (solo lo que te interesa)
  console.log('📤 AGRUPAR ENVIADO:', filtros.agrupar);

  // 🛡️ Payload explícito y seguro
  const payload = {
    desde: filtros.desde,
    hasta: filtros.hasta,
    agrupar: filtros.agrupar
  };

  return apiPost('/reportes', payload);
}


// Otros endpoints
export async function obtenerProductos() {
  return apiGet('/productos');
}

export async function obtenerPersonal() {
  return apiGet('/personal');
}

export async function obtenerDevoluciones(filtros = {}) {
  return apiGet('/devoluciones', filtros);
}


/* ───────── Helper opcional ───────── */

export function normalizarError(error) {
  return {
    mensaje: error.message || 'Error desconocido',
    timestamp: new Date().toISOString()
  };
}
