// profile.js - render perfil según rol (usa localStorage.userData)

document.addEventListener('DOMContentLoaded', () => {
    renderProfile();
});

function getUserFromStorage() {
    try {
        const raw = localStorage.getItem('userData');
        return raw ? JSON.parse(raw) : null;
    } catch (e) {
        console.error('Error parseando userData', e);
        return null;
    }
}

function renderProfile() {
    // Prefer server-injected user when available (authoritative). Fall back to localStorage.
    const user = (typeof window !== 'undefined' && window.serverUser) ? window.serverUser : getUserFromStorage();

    // If there's no user at all, show a message only if no server-rendered content exists.
    if (!user) {
        const root = document.getElementById('profile-root');
        if (root && root.textContent.trim() === '') {
            root.innerHTML = '<p class="text-red-600">No se encontró información de usuario. Inicia sesión.</p>';
        }
        return;
    }

    const role = user.role || 'solicitante';

    // helpers (defensive: only act on elements if present)
    const show = id => { const el = document.getElementById(id); if (el) el.style.display = 'block'; };
    const setText = (id, text) => { const el = document.getElementById(id); if (el) el.textContent = text; };
    const setHTML = (id, html) => { const el = document.getElementById(id); if (el) el.innerHTML = html; };

    if (role === 'solicitante') {
        show('profile-solicitante');
        setText('solicitante-name', `${user.first_name || ''} ${user.last_name || ''}`.trim());
        setText('solicitante-email', user.email || '');
        setHTML('solicitante-actions', `
            <a href="/requests" class="btn btn-primary">Mis Solicitudes</a>
            <a href="/solicitud-estandar/nueva" class="btn btn-secondary ml-2">Crear Nueva</a>
        `);
    } else if (role === 'aprobador') {
        show('profile-aprobador');
        setText('aprobador-name', `${user.first_name || ''} ${user.last_name || ''}`.trim());
        setText('aprobador-email', user.email || '');
        setHTML('aprobador-actions', `
            <a href="/dashboard-aprobador" class="btn btn-primary">Ir al Dashboard de Aprobador</a>
            <a href="/aprobador/api/pendientes" class="btn btn-secondary ml-2">Ver Pendientes (API)</a>
        `);
    } else if (role === 'pagador') {
        show('profile-pagador');
        setText('pagador-name', `${user.first_name || ''} ${user.last_name || ''}`.trim());
        setText('pagador-email', user.email || '');
        setHTML('pagador-actions', `
            <a href="/dashboard-pagador" class="btn btn-primary">Ir al Dashboard de Pagador</a>
            <a href="/pagador/api/pendientes-comprobante" class="btn btn-secondary ml-2">Ver Pendientes de Comprobante (API)</a>
        `);
    } else if (role === 'admin') {
        show('profile-admin');
        setText('admin-name', `${user.first_name || ''} ${user.last_name || ''}`.trim());
        setText('admin-email', user.email || '');
        setHTML('admin-actions', `
            <a href="/users" class="btn btn-primary">Gestionar Usuarios</a>
            <a href="/requests" class="btn btn-secondary ml-2">Ver Todas las Solicitudes</a>
        `);
    } else {
        // fallback
        show('profile-solicitante');
        setText('solicitante-name', `${user.first_name || ''} ${user.last_name || ''}`.trim());
        setText('solicitante-email', user.email || '');
    }

    // If serverUser is present, we won't overwrite the server-rendered details table. If not, we could optionally render extra fields here.
}
