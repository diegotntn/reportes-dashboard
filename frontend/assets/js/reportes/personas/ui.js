export function asegurarEstructuraContenedores(tab) {
  let controls = tab.querySelector('.personas-controls');
  if (!controls) {
    controls = document.createElement('div');
    controls.className = 'personas-controls';
    controls.style.cssText = `
      display:flex;gap:8px;flex-wrap:wrap;
      margin-bottom:20px;padding:12px;
      background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;
    `;
    tab.appendChild(controls);
  }

  let container = tab.querySelector('#personas-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'personas-container';
    container.style.cssText = 'min-height:400px;position:relative;';
    tab.appendChild(container);
  }
}

export function crearCanvas(container, altura = 400) {
  const wrap = document.createElement('div');
  wrap.style.cssText = `position:relative;width:100%;height:${altura}px;margin:20px 0;`;
  const canvas = document.createElement('canvas');
  wrap.appendChild(canvas);
  container.appendChild(wrap);
  return canvas;
}

export function crearSelector(labelText, opciones, valor, onChange) {
  const wrap = document.createElement('div');
  wrap.style.cssText = 'display:flex;gap:6px;align-items:center;';
  const label = document.createElement('span');
  label.textContent = labelText;
  const select = document.createElement('select');

  opciones.forEach(o => {
    const opt = document.createElement('option');
    opt.value = o;
    opt.textContent = o;
    opt.selected = o === valor;
    select.appendChild(opt);
  });

  select.addEventListener('change', e => onChange(e.target.value));

  wrap.append(label, select);
  return wrap;
}
