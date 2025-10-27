// Funciones principales para el sistema

// Configuración de la API
const API_BASE_URL = '/api';

// Utilidades
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('flash-messages');
    const alertId = 'alert-' + Date.now();
    
    const alertHTML = `
        <div id="${alertId}" class="alert alert-${type} fade-in">
            <div class="flex">
                <div class="flex-shrink-0">
                    <i class="fas ${getAlertIcon(type)}"></i>
                </div>
                <div class="ml-3">
                    <p class="text-sm">${message}</p>
                </div>
                <div class="ml-auto pl-3">
                    <button onclick="closeAlert('${alertId}')" class="text-gray-400 hover:text-gray-600">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    alertContainer.innerHTML = alertHTML;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        closeAlert(alertId);
    }, 5000);
}

function getAlertIcon(type) {
    switch(type) {
        case 'success': return 'fa-check-circle';
        case 'error': return 'fa-exclamation-circle';
        case 'warning': return 'fa-exclamation-triangle';
        default: return 'fa-info-circle';
    }
}

function closeAlert(alertId) {
    const alert = document.getElementById(alertId);
    if (alert) {
        alert.remove();
    }
}

// Función para realizar peticiones HTTP
async function apiRequest(url, options = {}) {
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };
    
    // Agregar token si existe (usar variables globales de auth.js)
    if (window.authToken) {
        config.headers['Authorization'] = `Bearer ${window.authToken}`;
    }
    
    try {
        // Ensure cookies (Set-Cookie) are accepted for same-origin requests
        if (!('credentials' in config)) {
            config.credentials = 'same-origin';
        }
        const response = await fetch(API_BASE_URL + url, config);
        
        if (!response.ok) {
            // Si es error 401 (Unauthorized), limpiar sesión y redirigir
            if (response.status === 401) {
                console.log('Token inválido o expirado, limpiando sesión...');
                if (typeof logout === 'function') {
                    logout();
                }
                return;
            }
            
            const errorData = await response.json().catch(() => ({ detail: 'Error desconocido' }));
            console.error('Error details:', errorData);
            throw new Error(JSON.stringify(errorData) || 'Error en la petición');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}

// Función para formatear fechas
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Función para obtener badge de estado
function getStatusBadge(status) {
    const badges = {
        'active': '<span class="badge badge-success"><i class="fas fa-check-circle mr-1"></i>Activo</span>',
        'inactive': '<span class="badge badge-warning"><i class="fas fa-pause-circle mr-1"></i>Inactivo</span>',
        'suspended': '<span class="badge badge-danger"><i class="fas fa-ban mr-1"></i>Suspendido</span>'
    };
    return badges[status] || '<span class="badge badge-secondary">Desconocido</span>';
}

// Función para obtener badge de rol
function getRoleBadge(role) {
    // Normalizar entrada para evitar problemas con mayúsculas/espacios
    const r = (role || '').toString().trim().toLowerCase();
    const badges = {
        'admin': '<span class="badge badge-info"><i class="fas fa-crown mr-1"></i>Administrador</span>',
        'solicitante': '<span class="badge badge-secondary"><i class="fas fa-user mr-1"></i>Solicitante</span>',
        'aprobador': '<span class="badge badge-primary"><i class="fas fa-user-check mr-1"></i>Aprobador</span>',
        'pagador': '<span class="badge badge-teal"><i class="fas fa-money-bill-wave mr-1"></i>Pagador</span>'
    };
    // Alias comunes: mapear variaciones a claves canónicas
    const alias = {
        'payer': 'pagador',
        'pay': 'pagador',
        'payment': 'pagador'
    };
    const key = badges[r] ? r : (alias[r] || r);
    return badges[key] || '<span class="badge badge-secondary">Desconocido</span>';
}

// Función para confirmar acciones
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Función para mostrar loading
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="text-center"><i class="fas fa-spinner fa-spin mr-2"></i>Cargando...</div>';
    }
}

// Función para ocultar loading
function hideLoading() {
    // Esta función se implementará según sea necesario
}

// Función para validar formularios
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('border-red-500');
            isValid = false;
        } else {
            field.classList.remove('border-red-500');
        }
    });
    
    return isValid;
}

// Función para limpiar formularios
function clearForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
        // Limpiar clases de error
        const errorFields = form.querySelectorAll('.border-red-500');
        errorFields.forEach(field => {
            field.classList.remove('border-red-500');
        });
    }
}

// Función para generar paginación
function generatePagination(currentPage, totalPages, onPageChange) {
    if (totalPages <= 1) return '';
    
    let paginationHTML = `
        <div class="flex items-center justify-between">
            <div class="flex-1 flex justify-between sm:hidden">
                <button onclick="${onPageChange}(${currentPage - 1})" ${currentPage <= 1 ? 'disabled' : ''} 
                        class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 ${currentPage <= 1 ? 'opacity-50 cursor-not-allowed' : ''}">
                    Anterior
                </button>
                <button onclick="${onPageChange}(${currentPage + 1})" ${currentPage >= totalPages ? 'disabled' : ''} 
                        class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 ${currentPage >= totalPages ? 'opacity-50 cursor-not-allowed' : ''}">
                    Siguiente
                </button>
            </div>
            <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                    <p class="text-sm text-gray-700">
                        Página <span class="font-medium">${currentPage}</span> de <span class="font-medium">${totalPages}</span>
                    </p>
                </div>
                <div>
                    <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
    `;
    
    // Botón anterior
    paginationHTML += `
        <button onclick="${onPageChange}(${currentPage - 1})" ${currentPage <= 1 ? 'disabled' : ''} 
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 ${currentPage <= 1 ? 'opacity-50 cursor-not-allowed' : ''}">
            <i class="fas fa-chevron-left"></i>
        </button>
    `;
    
    // Números de página
    for (let i = 1; i <= totalPages; i++) {
        if (i === currentPage) {
            paginationHTML += `
                <button class="bg-primary-50 border-primary-500 text-primary-600 relative inline-flex items-center px-4 py-2 border text-sm font-medium">
                    ${i}
                </button>
            `;
        } else if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            paginationHTML += `
                <button onclick="${onPageChange}(${i})" class="bg-white border-gray-300 text-gray-500 hover:bg-gray-50 relative inline-flex items-center px-4 py-2 border text-sm font-medium">
                    ${i}
                </button>
            `;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            paginationHTML += `
                <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                    ...
                </span>
            `;
        }
    }
    
    // Botón siguiente
    paginationHTML += `
        <button onclick="${onPageChange}(${currentPage + 1})" ${currentPage >= totalPages ? 'disabled' : ''} 
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 ${currentPage >= totalPages ? 'opacity-50 cursor-not-allowed' : ''}">
            <i class="fas fa-chevron-right"></i>
        </button>
                    </nav>
                </div>
            </div>
        </div>
    `;
    
    return paginationHTML;
}

// Inicialización cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    // Verificar si hay token guardado
    authToken = localStorage.getItem('authToken');
    
    // Configurar eventos globales
    setupGlobalEvents();
});

function setupGlobalEvents() {
    // Cerrar modales al hacer clic fuera
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal-overlay')) {
            closeModal();
        }
    });
    
    // Cerrar modales con Escape
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeModal();
        }
    });
}

// Función genérica para cerrar modales
function closeModal() {
    const modals = document.querySelectorAll('.modal-overlay');
    modals.forEach(modal => {
        modal.classList.add('hidden');
    });
}