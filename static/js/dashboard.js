// Dashboard - JavaScript específico para la página principal

// Variables globales
let dashboardData = {
    totalUsers: 0,
    totalRequests: 0,
    pendingRequests: 0,
    approvedRequests: 0,
    recentRequests: []
};

// Cargar dashboard cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    if (!requireAuth()) return;
    
    loadDashboardData();
    setupDashboardEvents();
    updateWelcomeMessage();
});

// Configurar eventos del dashboard
function setupDashboardEvents() {
    // Event listener para refresh
    const refreshButton = document.querySelector('[onclick="refreshDashboard()"]');
    if (refreshButton) {
        refreshButton.addEventListener('click', refreshDashboard);
    }
}

// Actualizar mensaje de bienvenida
function updateWelcomeMessage() {
    const welcomeElement = document.getElementById('welcomeMessage');
    if (welcomeElement && currentUser) {
        const timeOfDay = getTimeOfDay();
        welcomeElement.textContent = `¡${timeOfDay}, ${currentUser.first_name}!`;
    }
}

// Obtener saludo según la hora del día
function getTimeOfDay() {
    const hour = new Date().getHours();
    if (hour < 12) return 'Buenos días';
    if (hour < 18) return 'Buenas tardes';
    return 'Buenas noches';
}

// Cargar datos del dashboard
async function loadDashboardData() {
    try {
        // Mostrar loading en los contadores
        showLoadingCounters();
        
        // Cargar datos en paralelo
        const [usersData, userProfile] = await Promise.all([
            loadUsersStats(),
            loadUserProfile()
        ]);
        
        // Cargar solicitudes (simulado por ahora)
        loadRequestsStats();
        loadRecentRequests();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showAlert('Error al cargar datos del dashboard: ' + error.message, 'error');
    }
}

// Cargar estadísticas de usuarios
async function loadUsersStats() {
    try {
        const data = await apiRequest('/users?limit=1');
        dashboardData.totalUsers = data.total;
        
        // Actualizar contador
        document.getElementById('totalUsers').textContent = dashboardData.totalUsers;
        
        return data;
    } catch (error) {
        console.error('Error loading users stats:', error);
        document.getElementById('totalUsers').textContent = 'Error';
    }
}

// Cargar perfil del usuario
async function loadUserProfile() {
    try {
        const user = await apiRequest('/users/me');
        
        // Actualizar información del perfil en el sidebar
        updateUserProfileSidebar(user);
        
        return user;
    } catch (error) {
        console.error('Error loading user profile:', error);
        showUserProfileError();
    }
}

// Cargar estadísticas de solicitudes (simulado)
function loadRequestsStats() {
    // Por ahora simulamos datos ya que no tenemos el módulo de solicitudes
    dashboardData.totalRequests = Math.floor(Math.random() * 50) + 10;
    dashboardData.pendingRequests = Math.floor(Math.random() * 15) + 5;
    dashboardData.approvedRequests = dashboardData.totalRequests - dashboardData.pendingRequests;
    
    // Actualizar contadores
    document.getElementById('totalRequests').textContent = dashboardData.totalRequests;
    document.getElementById('pendingRequests').textContent = dashboardData.pendingRequests;
    document.getElementById('approvedRequests').textContent = dashboardData.approvedRequests;
}

// Cargar solicitudes recientes (simulado)
function loadRecentRequests() {
    // Simulamos solicitudes recientes
    const mockRequests = [
        {
            id: 1,
            title: 'Pago a proveedor de papelería',
            amount: '$2,500.00',
            status: 'pending',
            date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
            department: 'Administración'
        },
        {
            id: 2,
            title: 'Compra de equipos de cómputo',
            amount: '$45,000.00',
            status: 'approved',
            date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
            department: 'Tecnologías de la Información'
        },
        {
            id: 3,
            title: 'Pago de servicios de limpieza',
            amount: '$8,200.00',
            status: 'pending',
            date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
            department: 'Servicios Generales'
        }
    ];
    
    dashboardData.recentRequests = mockRequests;
    renderRecentRequests(mockRequests);
}

// Renderizar solicitudes recientes
function renderRecentRequests(requests) {
    const container = document.getElementById('recentRequests');
    
    if (!requests || requests.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-inbox mr-2"></i>
                No hay solicitudes recientes
            </div>
        `;
        return;
    }
    
    container.innerHTML = requests.map(request => `
        <div class="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
            <div class="flex-1">
                <div class="flex items-center justify-between">
                    <h4 class="text-sm font-medium text-gray-900">${request.title}</h4>
                    <span class="text-sm font-semibold text-green-600">${request.amount}</span>
                </div>
                <div class="mt-1 flex items-center text-xs text-gray-500">
                    <i class="fas fa-building mr-1"></i>
                    <span>${request.department}</span>
                    <span class="mx-2">•</span>
                    <i class="fas fa-calendar mr-1"></i>
                    <span>${formatDate(request.date)}</span>
                </div>
            </div>
            <div class="ml-4">
                ${getRequestStatusBadge(request.status)}
            </div>
        </div>
    `).join('');
}

// Obtener badge de estado de solicitud
function getRequestStatusBadge(status) {
    const badges = {
        'pending': '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800"><i class="fas fa-clock mr-1"></i>Pendiente</span>',
        'approved': '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"><i class="fas fa-check mr-1"></i>Aprobada</span>',
        'rejected': '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"><i class="fas fa-times mr-1"></i>Rechazada</span>'
    };
    return badges[status] || '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">Desconocido</span>';
}

// Actualizar perfil del usuario en el sidebar
function updateUserProfileSidebar(user) {
    const profileContainer = document.getElementById('userProfile');
    
    profileContainer.innerHTML = `
        <div class="flex items-center space-x-3 mb-3">
            <div class="flex-shrink-0">
                <div class="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                    <i class="fas fa-user text-primary-600"></i>
                </div>
            </div>
            <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">
                    ${user.first_name} ${user.last_name}
                </p>
                <p class="text-xs text-gray-500 truncate">
                    ${user.email}
                </p>
            </div>
        </div>
        
        <div class="space-y-2 text-sm">
            <div class="flex justify-between">
                <span class="text-gray-500">Departamento:</span>
                <span class="text-gray-900">${user.department}</span>
            </div>
            <div class="flex justify-between">
                <span class="text-gray-500">Rol:</span>
                ${getRoleBadge(user.role)}
            </div>
            <div class="flex justify-between">
                <span class="text-gray-500">Estado:</span>
                ${getStatusBadge(user.status)}
            </div>
            ${user.last_login ? `
                <div class="flex justify-between">
                    <span class="text-gray-500">Último acceso:</span>
                    <span class="text-gray-900">${formatDate(user.last_login)}</span>
                </div>
            ` : ''}
        </div>
        
        <div class="mt-4 pt-4 border-t border-gray-200">
            <button onclick="window.location.href='/profile'" class="w-full text-left px-3 py-2 text-sm text-primary-600 hover:bg-primary-50 rounded-md">
                <i class="fas fa-edit mr-2"></i>
                Editar Perfil
            </button>
        </div>
    `;
}

// Mostrar error en el perfil del usuario
function showUserProfileError() {
    const profileContainer = document.getElementById('userProfile');
    profileContainer.innerHTML = `
        <div class="text-center py-4 text-red-500">
            <i class="fas fa-exclamation-triangle mr-2"></i>
            Error al cargar perfil
        </div>
    `;
}

// Mostrar loading en los contadores
function showLoadingCounters() {
    const counters = ['totalUsers', 'totalRequests', 'pendingRequests', 'approvedRequests'];
    counters.forEach(counterId => {
        const element = document.getElementById(counterId);
        if (element) {
            element.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        }
    });
}

// Refrescar dashboard
function refreshDashboard() {
    showAlert('Actualizando dashboard...', 'info');
    loadDashboardData();
}

// Función para formatear fecha más simple
function formatDateSimple(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES');
}

// Obtener resumen de actividad reciente
function getActivitySummary() {
    const today = new Date();
    const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    // Simular actividad reciente
    return {
        newRequestsThisWeek: Math.floor(Math.random() * 10) + 1,
        approvedThisWeek: Math.floor(Math.random() * 8) + 1,
        pendingReview: Math.floor(Math.random() * 5) + 1
    };
}

// Función para mostrar tips o sugerencias
function showDashboardTips() {
    const tips = [
        'Puedes crear una nueva solicitud de pago desde el botón "Nueva Solicitud"',
        'Revisa regularmente el estado de tus solicitudes pendientes',
        'Los administradores pueden gestionar usuarios desde el menú "Usuarios"',
        'Mantén actualizada tu información de perfil',
        'Usa los filtros para encontrar solicitudes específicas rápidamente'
    ];
    
    const randomTip = tips[Math.floor(Math.random() * tips.length)];
    
    // Mostrar tip en notificaciones
    const notificationsContainer = document.getElementById('notifications');
    if (notificationsContainer) {
        const tipElement = document.createElement('div');
        tipElement.className = 'flex items-center p-3 bg-blue-50 rounded-lg mt-3';
        tipElement.innerHTML = `
            <div class="flex-shrink-0">
                <i class="fas fa-lightbulb text-blue-600"></i>
            </div>
            <div class="ml-3">
                <p class="text-sm text-blue-800">${randomTip}</p>
            </div>
        `;
        notificationsContainer.appendChild(tipElement);
    }
}

// Inicializar tips después de cargar
setTimeout(showDashboardTips, 3000);