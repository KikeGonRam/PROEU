// users.js - Gestión de usuarios CRUD

// Variables globales
let currentPage = 1;
let pageSize = 10;
let totalUsers = 0;
let totalPages = 0;
let currentFilters = {};
let editingUserId = null;
// Compatibilidad: alias usados en otras partes del código
let currentLimit = pageSize;
let currentTotal = totalUsers;

// Estado del modal
let isModalOpen = false;
let deleteUserId = null;

/**
 * Configuración de event listeners
 */
function setupEventListeners() {
    // Búsqueda en tiempo real
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                applyFilters();
            }, 500);
        });
    }

    // Form submission
    const userForm = document.getElementById('userForm');
    if (userForm) {
        userForm.addEventListener('submit', handleUserSubmit);
    }

    // Cerrar modal con ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (isModalOpen) {
                closeUserModal();
            }
            const deleteModal = document.getElementById('deleteModal');
            if (deleteModal && deleteModal.style.display !== 'none') {
                closeDeleteModal();
            }
        }
    });

    // Cerrar modal al hacer clic fuera
    const userModalEl = document.getElementById('userModal');
    if (userModalEl) {
        userModalEl.addEventListener('click', function(e) {
            if (e.target === this) {
                closeUserModal();
            }
        });
    }

    const deleteModalEl = document.getElementById('deleteModal');
    if (deleteModalEl) {
        deleteModalEl.addEventListener('click', function(e) {
            if (e.target === this) {
                closeDeleteModal();
            }
        });
    }
}

/**
 * Cargar lista de usuarios
 */
async function loadUsers(page = currentPage, limit = currentLimit, filters = currentFilters) {
    try {
        // Mostrar estado de carga en la UI
        const loadingEl = document.getElementById('loadingUsers');
        const usersContainer = document.getElementById('usersTableContainer');
        const emptyState = document.getElementById('emptyState');
        if (loadingEl) loadingEl.classList.remove('hidden');
        if (usersContainer) usersContainer.classList.add('hidden');
        if (emptyState) emptyState.classList.add('hidden');

        // Construir parámetros de consulta
        const params = new URLSearchParams({
            page: page,
            limit: limit,
            ... (filters || {})
        });

    const url = `/users?${params}`;
    console.log('loadUsers requesting URL:', url);
    const data = await apiRequest(url);
        // Debug: mostrar en consola los datos recibidos y los roles de los usuarios
        try {
            console.log('loadUsers params:', { page, limit, filters });
            console.log('loadUsers response:', data);
            console.log('loadUsers users roles:', (data && data.users) ? data.users.map(u => u.role) : []);
            if (data && data.users && data.users.length > 0) {
                console.log('loadUsers example user:', data.users[0]);
            }
        } catch (e) {
            console.warn('Error logging loadUsers debug info:', e);
        }

        // Actualizar estado local con seguridad
        currentPage = data.page || page;
        currentLimit = data.limit || limit;
        currentFilters = filters || {};
        // data.total puede venir como total o calcularse a partir de pages*limit
        currentTotal = data.total || (data.total_pages ? data.total_pages * currentLimit : currentTotal);

        // Renderizar tabla y paginación con comprobaciones DOM
        // Validar que la respuesta tenga la forma esperada
        const tbody = document.getElementById('usersTableBody');
        if (!data || !Array.isArray(data.users)) {
            console.warn('loadUsers: respuesta inesperada, se esperaba data.users array:', data);
            if (tbody) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="px-6 py-4 text-center text-gray-500">
                            No se pudieron obtener usuarios (respuesta inválida)
                        </td>
                    </tr>
                `;
            }
        } else {
            if (tbody) {
                renderUsersTable(data.users);
            } else {
                console.warn('users-table-body no encontrado en el DOM');
            }
        }

    const paginationContainer = document.getElementById('paginationNav');
        if (paginationContainer) {
            renderPagination(data);
        } else {
            console.warn('Contenedor de paginación no encontrado en el DOM');
        }

        // Mostrar resultados o estado vacío
        if (loadingEl) loadingEl.classList.add('hidden');
        if (data.users && data.users.length > 0) {
            if (usersContainer) usersContainer.classList.remove('hidden');
            if (emptyState) emptyState.classList.add('hidden');
        } else {
            if (usersContainer) usersContainer.classList.add('hidden');
            if (emptyState) emptyState.classList.remove('hidden');
        }

    } catch (error) {
        console.error('Error loading users:', error);
        showAlert('Error al cargar usuarios: ' + (error && error.message ? error.message : error), 'error');
        // Ocultar cargando y mostrar mensaje vacío/error
        const loadingEl = document.getElementById('loadingUsers');
        const usersContainer = document.getElementById('usersTableContainer');
        const emptyState = document.getElementById('emptyState');
        if (loadingEl) loadingEl.classList.add('hidden');
        if (usersContainer) usersContainer.classList.add('hidden');
        const tbody = document.getElementById('usersTableBody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="px-6 py-4 text-center text-red-500">
                        <i class="fas fa-exclamation-triangle mr-2"></i>
                        Error al cargar usuarios
                    </td>
                </tr>
            `;
        } else {
            console.warn('No se pudo mostrar el mensaje de error: users-table-body no existe');
        }
    }
}

// Renderizar tabla de usuarios
// Helper global: resolver badge de rol usando getRoleBadge y fallback local
function resolveRoleBadge(role) {
    try {
        let badge = (typeof getRoleBadge === 'function') ? getRoleBadge(role) : null;
        if (badge && !badge.includes('Desconocido')) return badge;
        const r = (role || '').toString().trim().toLowerCase();
        const local = {
            'pagador': '<span class="badge badge-teal"><i class="fas fa-money-bill-wave mr-1"></i>Pagador</span>',
            'aprobador': '<span class="badge badge-primary"><i class="fas fa-user-check mr-1"></i>Aprobador</span>',
            'admin': '<span class="badge badge-info"><i class="fas fa-crown mr-1"></i>Administrador</span>',
            'solicitante': '<span class="badge badge-secondary"><i class="fas fa-user mr-1"></i>Solicitante</span>'
        };
        return local[r] || badge || '<span class="badge badge-secondary">Desconocido</span>';
    } catch (e) {
        console.warn('resolveRoleBadge error:', e);
        return '<span class="badge badge-secondary">Desconocido</span>';
    }
}

function renderUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');
    
    if (users.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-4 text-center text-gray-500">
                    <i class="fas fa-users mr-2"></i>
                    No se encontraron usuarios
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = users.map(user => `
        <tr class="hover:bg-gray-50 transition-all">
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                        <div class="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                            <i class="fas fa-user text-primary-600"></i>
                        </div>
                    </div>
                    <div class="ml-4">
                        <div class="text-sm font-medium text-gray-900">
                            ${user.first_name} ${user.last_name}
                        </div>
                        <div class="text-sm text-gray-500">
                            ${user.email}
                        </div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ${user.department}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${resolveRoleBadge(user.role)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${getStatusBadge(user.status)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatDate(user.last_login)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex space-x-2">
                    <button onclick="editUser('${user.id || user._id}')" class="text-primary-600 hover:text-primary-900" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="deleteUser('${user.id || user._id}', '${user.first_name} ${user.last_name}')" class="text-red-600 hover:text-red-900" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                    <button onclick="toggleUserStatus('${user.id || user._id}', '${user.status}')" class="text-yellow-600 hover:text-yellow-900" title="Cambiar estado">
                        <i class="fas fa-toggle-${user.status === 'active' ? 'on' : 'off'}"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Renderizar paginación
function renderPagination(data) {
    const paginationContainer = document.getElementById('paginationNav');
    if (paginationContainer) {
        paginationContainer.innerHTML = generatePagination(data.page, data.total_pages, 'changePage');
    } else {
        console.warn('Contenedor de paginación no encontrado');
    }
}

// Cambiar página
function changePage(page) {
    const maxPage = currentLimit > 0 ? Math.ceil(currentTotal / currentLimit) : Infinity;
    if (page >= 1 && page <= maxPage) {
        loadUsers(page, currentLimit, currentFilters);
    } else {
        console.warn(`Página inválida solicitada: ${page} (max ${maxPage})`);
    }
}

// Aplicar filtros
function applyFilters() {
    const filters = {};
    
    const searchEl = document.getElementById('searchInput');
    const search = searchEl ? searchEl.value.trim() : '';
    if (search) filters.search = search;
    
    const roleEl = document.getElementById('roleFilter');
    const role = roleEl ? roleEl.value : '';
    // Normalizar role
    if (role) filters.role = role.toString().trim().toLowerCase();
    
    const statusEl = document.getElementById('statusFilter');
    const status = statusEl ? statusEl.value : '';
    if (status) filters.status = status.toString().trim().toLowerCase();
    
    currentPage = 1; // Reset to first page when filtering
    // Eliminar claves vacías (por si acaso)
    Object.keys(filters).forEach(k => {
        const v = filters[k];
        if (v === null || v === undefined || (typeof v === 'string' && v.trim() === '')) delete filters[k];
    });
    console.log('applyFilters built filters:', filters);
    loadUsers(currentPage, currentLimit, filters);
}

// Abrir modal para crear usuario
function openCreateModal() {
    isEditMode = false;
    const modalTitle = document.getElementById('modalTitle');
    if (modalTitle) modalTitle.textContent = 'Nuevo Usuario';
    const submitButtonText = document.getElementById('submitButtonText');
    if (submitButtonText) submitButtonText.textContent = 'Crear Usuario';
    const passwordLabel = document.getElementById('passwordLabel');
    if (passwordLabel) passwordLabel.textContent = 'Contraseña *';
    const passwordHelp = document.getElementById('passwordHelp');
    if (passwordHelp) passwordHelp.textContent = 'Mínimo 6 caracteres';
    const passwordInput = document.getElementById('password');
    if (passwordInput) passwordInput.required = true;
    clearForm('userForm');
    const userModal = document.getElementById('userModal');
    if (userModal) userModal.classList.remove('hidden');
    // Mostrar passwordBlock enfatizado para creación
    const passwordBlock = document.getElementById('passwordBlock');
    if (passwordBlock) {
        passwordBlock.classList.remove('bg-gray-50','border-gray-200');
        passwordBlock.classList.add('bg-yellow-100','border-yellow-400');
    }
}

// Abrir modal para editar usuario
async function editUser(userId) {
    try {
        isEditMode = true;
        const modalTitle = document.getElementById('modalTitle');
        if (modalTitle) modalTitle.textContent = 'Editar Usuario';
        const submitButtonText = document.getElementById('submitButtonText');
        if (submitButtonText) submitButtonText.textContent = 'Actualizar Usuario';
        const passwordLabel = document.getElementById('passwordLabel');
        if (passwordLabel) passwordLabel.textContent = 'Nueva Contraseña (opcional)';
        const passwordHelp = document.getElementById('passwordHelp');
        if (passwordHelp) passwordHelp.textContent = 'Dejar vacío para mantener la contraseña actual';
        const passwordInput = document.getElementById('password');
        if (passwordInput) passwordInput.required = false;
        // Cargar datos del usuario
        const user = await apiRequest(`/users/${userId}`);
        // Llenar formulario
    const userIdInput = document.getElementById('userId');
    if (userIdInput) userIdInput.value = user.id || user._id;
        const firstNameInput = document.getElementById('firstName');
        if (firstNameInput) firstNameInput.value = user.first_name;
        const lastNameInput = document.getElementById('lastName');
        if (lastNameInput) lastNameInput.value = user.last_name;
        const emailInput = document.getElementById('email');
        if (emailInput) emailInput.value = user.email;
        const departmentInput = document.getElementById('department');

    
        if (departmentInput) departmentInput.value = user.department;
        const phoneInput = document.getElementById('phone');
        if (phoneInput) phoneInput.value = user.phone || '';
        const roleInput = document.getElementById('role');
        if (roleInput) roleInput.value = user.role;
        const statusInput = document.getElementById('status');
        if (statusInput) statusInput.value = user.status;
        if (passwordInput) passwordInput.value = '';
        const userModal = document.getElementById('userModal');
        if (userModal) userModal.classList.remove('hidden');
        // Mostrar passwordBlock neutral para edición
        const passwordBlock = document.getElementById('passwordBlock');
        if (passwordBlock) {
            passwordBlock.classList.remove('bg-yellow-100','border-yellow-400');
            passwordBlock.classList.add('bg-gray-50','border-gray-200');
        }
    } catch (error) {
        console.error('Error loading user:', error);
        showAlert('Error al cargar usuario: ' + error.message, 'error');
    }
}

// Cerrar modal
function closeModal() {
    document.getElementById('userModal').classList.add('hidden');
    clearForm('userForm');
}

// Manejar envío del formulario
async function handleUserSubmit(event) {
    event.preventDefault();
    
    if (!validateForm('userForm')) {
        showAlert('Por favor, complete todos los campos requeridos', 'warning');
        return;
    }
    
    try {
        const formData = new FormData(event.target);
        const userData = {};
        
        // Recopilar datos del formulario
        userData.first_name = formData.get('firstName');
        userData.last_name = formData.get('lastName');
        userData.email = formData.get('email');
        userData.department = formData.get('department');
        userData.phone = formData.get('phone') || null;
        userData.role = formData.get('role');
        userData.status = formData.get('status');
        
        const password = formData.get('password');
        if (password) {
            userData.password = password;
        }
        
        let response;
        if (isEditMode) {
            const userId = formData.get('userId');
            if (!userId) {
                showAlert('ID de usuario no proporcionado', 'error');
                return;
            }
            response = await apiRequest(`/users/${userId}`, {
                method: 'PUT',
                body: JSON.stringify(userData)
            });
            showAlert('Usuario actualizado exitosamente', 'success');
        } else {
            response = await apiRequest('/users', {
                method: 'POST',
                body: JSON.stringify(userData)
            });
            showAlert('Usuario creado exitosamente', 'success');
        }
        
        closeModal();
        loadUsers(currentPage, currentLimit, currentFilters);
        
    } catch (error) {
        console.error('Error saving user:', error);
        showAlert('Error al guardar usuario: ' + error.message, 'error');
    }
}

// Eliminar usuario
function deleteUser(userId, userName) {
    confirmAction(
        `¿Está seguro de que desea eliminar al usuario "${userName}"? Esta acción no se puede deshacer.`,
        async () => {
            try {
                await apiRequest(`/users/${userId}`, {
                    method: 'DELETE'
                });
                
                showAlert('Usuario eliminado exitosamente', 'success');
                loadUsers(currentPage, currentLimit, currentFilters);
                
            } catch (error) {
                console.error('Error deleting user:', error);
                showAlert('Error al eliminar usuario: ' + error.message, 'error');
            }
        }
    );
}

// Cambiar estado de usuario
async function toggleUserStatus(userId, currentStatus) {
    try {
        const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
        
        await apiRequest(`/users/${userId}/status?status=${newStatus}`, {
            method: 'PATCH'
        });
        
        showAlert(`Estado del usuario cambiado a ${newStatus === 'active' ? 'activo' : 'inactivo'}`, 'success');
        loadUsers(currentPage, currentLimit, currentFilters);
        
    } catch (error) {
        console.error('Error changing user status:', error);
        showAlert('Error al cambiar estado del usuario: ' + error.message, 'error');
    }
}

// Exportar usuarios (función futura)
function exportUsers() {
    showAlert('Función de exportación en desarrollo', 'info');
}

// -----------------------------
// Compatibilidad con nombres antiguos usados en plantillas
// Algunas plantillas llaman a `openAddUserModal` y `closeUserModal`.
// Mantener wrappers para evitar errores ReferenceError.
function openAddUserModal() {
    if (typeof openCreateModal === 'function') return openCreateModal();
    console.warn('openCreateModal no está disponible');
}

function closeUserModal() {
    if (typeof closeModal === 'function') return closeModal();
    console.warn('closeModal no está disponible');
}
