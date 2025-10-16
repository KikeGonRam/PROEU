// settings.js - mostrar opciones de configuración por rol (usa localStorage.userData)

document.addEventListener('DOMContentLoaded', () => {
    renderSettings();
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

function renderSettings() {
    // Prefer server-injected user when available
    const user = (typeof window !== 'undefined' && window.serverUser) ? window.serverUser : getUserFromStorage();

    const root = document.getElementById('settings-root');
    if (!user) {
        if (root && root.textContent.trim() === '') {
            root.innerHTML = '<p class="text-red-600">No se encontró información de usuario. Inicia sesión.</p>';
        }
        return;
    }

    const role = user.role || 'solicitante';

    const show = id => { const el = document.getElementById(id); if (el) el.style.display = 'block'; };
    const setHTML = (id, html) => { const el = document.getElementById(id); if (el) el.innerHTML = html; };

    const commonPrefs = `
        <div class="mb-4">
            <label class="block text-sm font-medium">Notificaciones por email</label>
            <input type="checkbox" id="pref-email" />
        </div>
        <div class="mb-4">
            <label class="block text-sm font-medium">Zona horaria</label>
            <select id="pref-tz"><option>UTC</option><option>America/Mexico_City</option></select>
        </div>
    `;

    if (role === 'solicitante') {
        show('settings-solicitante');
        setHTML('prefs-solicitante', commonPrefs + '<div class="mb-4">Preferencias específicas de solicitante</div>');
    } else if (role === 'aprobador') {
        show('settings-aprobador');
        setHTML('prefs-aprobador', commonPrefs + '<div class="mb-4">Notificaciones de aprobaciones y rechazos</div>');
    } else if (role === 'pagador') {
        show('settings-pagador');
        setHTML('prefs-pagador', commonPrefs + '<div class="mb-4">Preferencias de método de pago</div>');
    } else if (role === 'admin') {
        show('settings-admin');
        setHTML('prefs-admin', commonPrefs + '<div class="mb-4">Preferencias globales y herramientas de administración</div>');
    } else {
        show('settings-solicitante');
        setHTML('prefs-solicitante', commonPrefs);
    }
}
