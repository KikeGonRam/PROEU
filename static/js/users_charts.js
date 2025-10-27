// users_charts.js - Render charts for users

async function fetchJSON(url) {
    try {
        const res = await apiRequest(url);
        return res && res.data ? res.data : null;
    } catch (e) {
        console.error('Error fetching', url, e);
        return null;
    }
}

function createPieChart(ctx, labels, data, colors) {
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors || undefined,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '40%',
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12, padding: 12, usePointStyle: true } },
                tooltip: { padding: 10 }
            },
            layout: { padding: 12 }
        }
    });
}

function createLineChart(ctx, labels, data) {
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cantidad',
                data: data,
                fill: true,
                backgroundColor: 'rgba(79,70,229,0.12)',
                borderColor: 'rgba(79,70,229,1)',
                pointRadius: 3,
                pointHoverRadius: 6,
                tension: 0.25
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false }, tooltip: { mode: 'index', intersect: false } },
            scales: {
                x: { ticks: { color: '#374151', maxRotation: 0, autoSkip: true } },
                y: { beginAtZero: true, ticks: { color: '#374151' } }
            },
            layout: { padding: 8 }
        }
    });
}

function createBarChart(ctx, labels, data) {
    return new Chart(ctx, {
        type: 'bar',
        data: { labels: labels, datasets: [{ label: 'Usuarios', data: data, backgroundColor: 'rgba(6,182,212,0.9)', borderRadius: 6, barThickness: 18 }] },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: { legend: { display: false }, tooltip: { padding: 8 } },
            scales: {
                x: { beginAtZero: true, ticks: { color: '#374151' } },
                y: { ticks: { color: '#374151' } }
            },
            layout: { padding: 8 }
        }
    });
}

// Utility to get drawing context and ensure parent has explicit height
function getCanvasContextById(id) {
    const canvas = document.getElementById(id);
    if (!canvas) return null;
    // Make sure parent container has explicit height so Chart.js can size properly
    const parent = canvas.parentElement;
    if (parent && !parent.style.height) {
        parent.style.height = '320px';
    }
    return canvas.getContext('2d');
}

async function renderCharts() {
    // Roles
    const rolesData = await fetchJSON('/users/stats/roles');
    const rolesCtx = getCanvasContextById('chartRoles');
    if (rolesData && rolesCtx) {
        createPieChart(rolesCtx, rolesData.labels, rolesData.datasets[0].data, ['#4F46E5','#06B6D4','#10B981','#F59E0B','#EF4444']);
    }

    // Registrations
    const regsData = await fetchJSON('/users/stats/registrations?period=month');
    const regsCtx = getCanvasContextById('chartRegistrations');
    if (regsData && regsCtx) {
        createLineChart(regsCtx, regsData.labels, regsData.datasets[0].data);
    }

    // Last logins
    const lastData = await fetchJSON('/users/stats/last_logins');
    const lastCtx = getCanvasContextById('chartLastLogins');
    if (lastData && lastCtx) {
        createBarChart(lastCtx, lastData.labels, lastData.datasets[0].data);
    }

    // Departments
    const deptData = await fetchJSON('/users/stats/departments?top=10');
    const deptCtx = getCanvasContextById('chartDepartments');
    if (deptData && deptCtx) {
        createBarChart(deptCtx, deptData.labels, deptData.datasets[0].data);
    }
}

// in case the page loads after DOM ready
document.addEventListener('DOMContentLoaded', function() {
    // Ensure apiRequest is available (from main.js)
    if (typeof apiRequest !== 'function') {
        console.error('apiRequest helper not found. Ensure main.js is loaded.');
        return;
    }
    renderCharts();
});
