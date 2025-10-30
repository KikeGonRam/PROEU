// requests_charts.js - Render charts for solicitudes (uses aggregated endpoint)

async function fetchRequestsDetalle() {
    try {
        return await apiRequest('/solicitudes/estadisticas/detalle');
    } catch (e) {
        console.error('Error fetching solicitudes detalle:', e);
        return null;
    }
}

function createPieChart(ctx, labels, data, colors) {
    return new Chart(ctx, {
        type: 'doughnut',
        data: { labels: labels, datasets: [{ data: data, backgroundColor: colors || undefined, borderWidth: 0 }] },
        options: { responsive: true, maintainAspectRatio: false, cutout: '40%', plugins: { legend: { position: 'bottom' } } }
    });
}

function createBarChart(ctx, labels, data, color) {
    return new Chart(ctx, {
        type: 'bar',
        data: { labels: labels, datasets: [{ label: 'Cantidad', data: data, backgroundColor: color || 'rgba(6,182,212,0.9)', borderRadius: 6 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true }, y: { ticks: { color: '#374151' } } } }
    });
}

function getCanvasContextById(id) {
    const canvas = document.getElementById(id);
    if (!canvas) return null;
    const parent = canvas.parentElement;
    if (parent && !parent.style.height) parent.style.height = '320px';
    return canvas.getContext('2d');
}

async function renderRequestCharts() {
    const resp = await fetchRequestsDetalle();
    if (!resp) return;

    const by_state = resp.by_state || [];
    const by_type = resp.by_type || [];
    const by_month = resp.by_month || [];
    const summary = resp.summary || { total: 0, monto_total: 0 };

    const stateLabelsMap = {
        'borrador': 'Borrador',
        'enviada': 'Enviada',
        'en_revision': 'En Revisión',
        'aprobada': 'Aprobada',
        'rechazada': 'Rechazada',
        'pagada': 'Pagada',
        'cancelada': 'Cancelada'
    };

    const stateLabels = by_state.map(s => stateLabelsMap[s._id] || s._id);
    const stateCounts = by_state.map(s => s.count || 0);
    const stateAmounts = by_state.map(s => s.total_monto || 0);

    // Summary
    const totalEl = document.getElementById('totalSolicitudes');
    if (totalEl) totalEl.textContent = summary.total;
    const pendientesEl = document.getElementById('pendientes');
    if (pendientesEl) pendientesEl.textContent = by_state.filter(s => ['enviada','en_revision'].includes(s._id)).reduce((a,b)=>a+(b.count||0),0);
    const aprobadasEl = document.getElementById('aprobadas');
    if (aprobadasEl) aprobadasEl.textContent = by_state.filter(s => s._id === 'aprobada').reduce((a,b)=>a+(b.count||0),0);
    const montoEl = document.getElementById('montoTotal');
    if (montoEl) montoEl.textContent = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(summary.monto_total || 0);

    const statesCtx = getCanvasContextById('chartStates');
    if (statesCtx && stateLabels.length) createPieChart(statesCtx, stateLabels, stateCounts, ['#4F46E5','#06B6D4','#10B981','#F59E0B','#EF4444','#8B5CF6','#94A3B8']);

    const amountsCtx = getCanvasContextById('chartAmounts');
    if (amountsCtx && stateLabels.length) createBarChart(amountsCtx, stateLabels, stateAmounts, 'rgba(79,70,229,0.9)');

    const typeLabels = by_type.map(t => t._id || 'Otros');
    const typeCounts = by_type.map(t => t.count || 0);
    const typesCtx = getCanvasContextById('chartTypes');
    if (typesCtx && typeLabels.length) createBarChart(typesCtx, typeLabels, typeCounts, 'rgba(6,182,212,0.9)');

    // (Optional) implement a line chart for by_month if desired
}

// Start
document.addEventListener('DOMContentLoaded', function() {
    if (typeof apiRequest !== 'function') { console.error('apiRequest helper not found. Ensure main.js is loaded.'); return; }
    renderRequestCharts();
});
