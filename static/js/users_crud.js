// users.js - Gestión de usuarios CRUD

// Variables globales
let currentPage = 1;
let pageSize = 10;
let totalUsers = 0;
let totalPages = 0;
let currentFilters = {};
let editingUserId = null;

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
    document.getElementById('userModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeUserModal();
        }
    });

    document.getElementById('deleteModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeDeleteModal();
        }
    });
}

/**
 * Cargar lista de usuarios
 */
async function loadUsers() {
    try {
        showLoading();
        
        // Construir parámetros de consulta
        const params = new URLSearchParams({
            page: currentPage,
            limit: pageSize,
            ...currentFilters
        });
        
        const data = await apiRequest(`/users?${params}`);
        
        currentPage = data.page;
        currentLimit = data.limit;
        currentFilters = filters;
        
        renderUsersTable(data.users);
        renderPagination(data);
        
    } catch (error) {
        console.error('Error loading users:', error);
        showAlert('Error al cargar usuarios: ' + error.message, 'error');
        document.getElementById('users-table-body').innerHTML = `
            <tr>
                <td colspan="6" class="px-6 py-4 text-center text-red-500">
                    <i class="fas fa-exclamation-triangle mr-2"></i>
                    Error al cargar usuarios
                </td>
            </tr>
        `;
    }
}

// Renderizar tabla de usuarios
function renderUsersTable(users) {
    const tbody = document.getElementById('users-table-body');
    
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
                ${getRoleBadge(user.role)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                ${getStatusBadge(user.status)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatDate(user.last_login)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex space-x-2">
                    <button onclick="editUser('${user.id}')" class="text-primary-600 hover:text-primary-900" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button onclick="deleteUser('${user.id}', '${user.first_name} ${user.last_name}')" class="text-red-600 hover:text-red-900" title="Eliminar">
                        <i class="fas fa-trash"></i>
                    </button>
                    <button onclick="toggleUserStatus('${user.id}', '${user.status}')" class="text-yellow-600 hover:text-yellow-900" title="Cambiar estado">
                        <i class="fas fa-toggle-${user.status === 'active' ? 'on' : 'off'}"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Renderizar paginación
function renderPagination(data) {
    const paginationContainer = document.getElementById('pagination');
    paginationContainer.innerHTML = generatePagination(data.page, data.total_pages, 'changePage');
}

// Cambiar página
function changePage(page) {
    if (page >= 1 && page <= Math.ceil(currentTotal / currentLimit)) {
        loadUsers(page, currentLimit, currentFilters);
    }
}

// Aplicar filtros
function applyFilters() {
    const filters = {};
    
    const search = document.getElementById('search').value.trim();
    if (search) filters.search = search;
    
    const role = document.getElementById('role-filter').value;
    if (role) filters.role = role;
    
    const status = document.getElementById('status-filter').value;
    if (status) filters.status = status;
    
    currentPage = 1; // Reset to first page when filtering
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
        if (userIdInput) userIdInput.value = user.id;
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