// aprobador_charts.js - Render charts for Aprobador dashboard using detailed aggregated endpoint

async function fetchAprobadorDetalle() {
    try {
        const token = localStorage.getItem('authToken');
        const res = await fetch('/aprobador/api/estadisticas/detalle', {
            headers: {
                'Authorization': token ? `Bearer ${token}` : ''
            }
        });
        if (!res.ok) throw new Error('Error fetching aprobador detalle');
        return await res.json();
    } catch (e) {
        console.error('Error fetching aprobador detalle:', e);
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
    if (parent && !parent.style.height) parent.style.height = '300px';
    return canvas.getContext('2d');
}

async function renderAprobadorCharts() {
    const resp = await fetchAprobadorDetalle();
    if (!resp) return;

    const by_state = resp.by_state || [];
    const by_type = resp.by_type || [];
    const by_month = resp.by_month || [];
    const summary = resp.summary || {};

    // Update summary cards if present
    if (summary) {
        const pendientesEl = document.getElementById('stat-pendientes');
        if (pendientesEl && typeof summary.pendientes !== 'undefined') pendientesEl.textContent = summary.pendientes;
        const aprobadasEl = document.getElementById('stat-aprobadas');
        if (aprobadasEl && typeof summary.aprobadas !== 'undefined') aprobadasEl.textContent = summary.aprobadas;
        const rechazadasEl = document.getElementById('stat-rechazadas');
        if (rechazadasEl && typeof summary.rechazadas !== 'undefined') rechazadasEl.textContent = summary.rechazadas;
        const montoEl = document.getElementById('stat-monto');
        if (montoEl && typeof summary.monto_pendiente !== 'undefined') montoEl.textContent = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(summary.monto_pendiente);
    }

    const stateLabels = by_state.map(s => s._id || 'Desconocido');
    const stateCounts = by_state.map(s => s.count || 0);
    const stateAmounts = by_state.map(s => s.total_monto || 0);

    const statesCtx = getCanvasContextById('chartAprobStates');
    if (statesCtx && stateLabels.length) createPieChart(statesCtx, stateLabels, stateCounts, ['#4F46E5','#06B6D4','#10B981','#F59E0B','#EF4444','#8B5CF6','#94A3B8']);

    const amountsCtx = getCanvasContextById('chartAprobAmounts');
    if (amountsCtx && stateLabels.length) createBarChart(amountsCtx, stateLabels, stateAmounts, 'rgba(79,70,229,0.9)');

    const typeLabels = by_type.map(t => t._id || 'Otros');
    const typeCounts = by_type.map(t => t.count || 0);
    const typesCtx = getCanvasContextById('chartAprobTypes');
    if (typesCtx && typeLabels.length) createBarChart(typesCtx, typeLabels, typeCounts, 'rgba(6,182,212,0.9)');
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Delay slightly to allow aprobador.js to set tokens/local state
    setTimeout(() => {
        renderAprobadorCharts();
    }, 300);
});
