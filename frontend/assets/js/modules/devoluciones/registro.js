import { apiGet, apiPost } from '../../api.js';
import { state } from '../../state.js';

/**
 * Registro de devoluciones
 *
 * RESPONSABILIDADES:
 * - Cargar vista y subcomponentes
 * - Orquestar formularios y tabla
 * - Delegar reglas al backend
 *
 * NO:
 * - Validaciones de negocio complejas
 * - Lógica de API fuera de api.js
 */

// ─────────────────────────────────────────────
// Entrada principal
// ─────────────────────────────────────────────
export async function cargarRegistro() {
  const mount = document.getElementById('devoluciones-subview');
  if (!mount) return;

  const html = await fetch('views/devoluciones_registro.html').then(r => r.text());
  mount.innerHTML = html;

  _initLocalState();
  await _loadComponents();
  await _preloadData();
  _bindEvents();
}

// ─────────────────────────────────────────────
// Estado local del registro (equiv. atributos Tk)
// ─────────────────────────────────────────────
function _initLocalState() {
  state.articulos = [];
}

// ─────────────────────────────────────────────
// Cargar subcomponentes visuales
// ─────────────────────────────────────────────
async function _loadComponents() {
  const [registroForm, articuloForm, tabla] = await Promise.all([
    fetch('components/registro_form.html').then(r => r.text()),
    fetch('components/articulo_form.html').then(r => r.text()),
    fetch('components/articulos_table.html').then(r => r.text())
  ]);

  document.getElementById('registro-form-container').innerHTML = registroForm;
  document.getElementById('articulo-form-container').innerHTML = articuloForm;
  document.getElementById('articulos-table-container').innerHTML = tabla;
}

// ─────────────────────────────────────────────
// Precarga de datos (equiv. productos_service)
// ─────────────────────────────────────────────
async function _preloadData() {
  try {
    state.productos = await apiGet('/productos');
    _cargarProductosSelect(state.productos);
  } catch (e) {
    _setError('No se pudieron cargar los productos');
  }
}

function _cargarProductosSelect(productos) {
  const select = document.querySelector('[name="producto_id"]');
  if (!select) return;

  select.innerHTML = `
    <option value="">Seleccione un producto</option>
    ${productos.map(p => `
      <option value="${p.id}">
        ${p.nombre}
      </option>
    `).join('')}
  `;
}

// ─────────────────────────────────────────────
// Eventos UI (equiv. RegistroEvents.bind)
// ─────────────────────────────────────────────
function _bindEvents() {
  document
    .getElementById('btn-agregar-articulo')
    ?.addEventListener('click', _onAgregarArticulo);

  document
    .getElementById('btn-guardar-devolucion')
    ?.addEventListener('click', _onGuardar);

  // Delegación para quitar artículos
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('[data-art-remove]');
    if (!btn) return;

    const index = Number(btn.dataset.artRemove);
    _quitarArticulo(index);
  });
}

// ─────────────────────────────────────────────
// Lógica de interacción (equiv. methods Events)
// ─────────────────────────────────────────────
function _onAgregarArticulo() {
  _clearError();

  const articulo = _leerArticuloForm();
  if (!articulo) return;

  state.articulos.push(articulo);
  _renderArticulos();
  _limpiarArticuloForm();
}

async function _onGuardar() {
  _clearError();

  const devolucion = _leerRegistroForm();
  if (!devolucion) return;

  if (state.articulos.length === 0) {
    _setError('Debe agregar al menos un artículo');
    return;
  }

  const payload = {
    ...devolucion,
    articulos: state.articulos
  };

  try {
    await apiPost('/devoluciones', payload);

    // Evento semántico (equiv. on_saved)
    document.dispatchEvent(
      new CustomEvent('devolucion:saved')
    );

  } catch (e) {
    _setError('No se pudo guardar la devolución');
  }
}

// ─────────────────────────────────────────────
// Lectura de formularios
// ─────────────────────────────────────────────
function _leerRegistroForm() {
  const fecha = document.querySelector('[name="fecha"]')?.value;
  const vendedor = document.querySelector('[name="vendedor_id"]')?.value;
  const zona = document.querySelector('[name="zona"]')?.value;
  const observaciones = document.querySelector('[name="observaciones"]')?.value;

  if (!fecha) {
    _setError('La fecha es obligatoria');
    return null;
  }

  return {
    fecha,
    vendedor_id: vendedor || null,
    zona: zona || null,
    observaciones: observaciones || null
  };
}

function _leerArticuloForm() {
  const producto = document.querySelector('[name="producto_id"]')?.value;
  const cantidad = Number(document.querySelector('[name="cantidad"]')?.value);
  const motivo = document.querySelector('[name="motivo"]')?.value;
  const lote = document.querySelector('[name="lote"]')?.value;

  if (!producto || !cantidad || cantidad <= 0) {
    _setError('Producto y cantidad válidos son obligatorios');
    return null;
  }

  return {
    producto_id: producto,
    cantidad,
    motivo: motivo || null,
    lote: lote || null
  };
}

// ─────────────────────────────────────────────
// Tabla de artículos (equiv. ArticulosTable)
// ─────────────────────────────────────────────
function _renderArticulos() {
  const tbody = document.querySelector('#articulos-table tbody');
  const empty = document.getElementById('articulos-empty');

  if (!tbody) return;

  tbody.innerHTML = '';

  if (state.articulos.length === 0) {
    empty && (empty.style.display = 'block');
    return;
  }

  empty && (empty.style.display = 'none');

  state.articulos.forEach((a, i) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${a.producto_id}</td>
      <td>${a.cantidad}</td>
      <td>${a.motivo || '-'}</td>
      <td>${a.lote || '-'}</td>
      <td>
        <button
          class="btn btn--small btn--danger"
          data-art-remove="${i}">
          Quitar
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function _quitarArticulo(index) {
  state.articulos.splice(index, 1);
  _renderArticulos();
}

// ─────────────────────────────────────────────
// Utilidades UI
// ─────────────────────────────────────────────
function _limpiarArticuloForm() {
  ['producto_id', 'cantidad', 'motivo', 'lote'].forEach(name => {
    const el = document.querySelector(`[name="${name}"]`);
    if (el) el.value = '';
  });
}

function _setError(msg) {
  const el = document.getElementById('registro-error');
  if (!el) return;

  el.textContent = msg;
  el.hidden = false;
}

function _clearError() {
  const el = document.getElementById('registro-error');
  if (el) el.hidden = true;
}
