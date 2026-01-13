export function estadoVacio(msg) {
  return `
    <div style="padding:60px;text-align:center;color:#64748b">
      <div style="font-size:48px">📊</div>
      <h3>Reporte por Personas</h3>
      <p>${msg}</p>
    </div>
  `;
}

export function mostrarEstadoEspera() {
  const tab = document.getElementById('tab-personas');
  if (!tab) return;
  const container = tab.querySelector('#personas-container');
  if (container) container.innerHTML = estadoVacio('Esperando datos del reporte...');
}
