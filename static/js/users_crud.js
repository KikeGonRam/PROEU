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
let currentDetailUserId = null;

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
            if (document.getElementById('deleteModal').classList.contains('hidden') === false) {
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

        const response = await apiRequest(`/users?${params.toString()}`, {
            method: 'GET'
        });

        if (response.users) {
            displayUsers(response.users);
            
            // Crear objeto de paginación compatible
            const pagination = {
                total: response.total,
                pages: response.total_pages,
                page: response.page
            };
            
            updatePagination(pagination);
            updateUserCount(response.total);
        } else {
            throw new Error('Formato de respuesta inválido');
        }

    } catch (error) {
        console.error('Error loading users:', error);
        showError('Error al cargar usuarios: ' + error.message);
        showEmptyState();
    }
}

/**
 * Mostrar estado de carga
 */
function showLoading() {
    document.getElementById('loadingUsers').classList.remove('hidden');
    document.getElementById('usersTableContainer').classList.add('hidden');
    document.getElementById('emptyState').classList.add('hidden');
}

/**
 * Mostrar usuarios en la tabla
 */
function displayUsers(users) {
    const tbody = document.getElementById('usersTableBody');
    const tableContainer = document.getElementById('usersTableContainer');
    const loadingDiv = document.getElementById('loadingUsers');
    const emptyState = document.getElementById('emptyState');

    loadingDiv.classList.add('hidden');

    if (!users || users.length === 0) {
        tableContainer.classList.add('hidden');
        emptyState.classList.remove('hidden');
        return;
    }

    emptyState.classList.add('hidden');
    tableContainer.classList.remove('hidden');

    tbody.innerHTML = '';

    users.forEach(user => {
        const row = createUserRow(user);
        tbody.appendChild(row);
    });
}

/**
 * Crear fila de usuario
 */
function createUserRow(user) {
    const tr = document.createElement('tr');
    tr.className = 'hover:bg-gray-50';

    // Formatear fecha de último acceso
    const lastLogin = user.last_login ? 
        new Date(user.last_login).toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }) : 'Nunca';

    tr.innerHTML = `
        <td class="px-6 py-4 whitespace-nowrap">
            <div class="flex items-center">
                <div class="flex-shrink-0 h-10 w-10">
                    <div class="h-10 w-10 rounded-full bg-primary-100 flex items-center justify-center">
                        <span class="text-sm font-medium text-primary-700">
                            ${(user.first_name?.charAt(0) || '').toUpperCase()}${(user.last_name?.charAt(0) || '').toUpperCase()}
                        </span>
                    </div>
                </div>
                <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">
                        ${user.first_name || ''} ${user.last_name || ''}
                    </div>
                    <div class="text-sm text-gray-500">
                        ${user.email || ''}
                    </div>
                    ${user.phone ? `<div class="text-xs text-gray-400">${user.phone}</div>` : ''}
                </div>
            </div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
            <div class="text-sm text-gray-900">${user.department || 'No asignado'}</div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeClass(user.role)}">
                <i class="fas ${getRoleIcon(user.role)} mr-1"></i>
                ${getRoleLabel(user.role)}
            </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeClass(user.status)}">
                <span class="w-1.5 h-1.5 rounded-full ${getStatusDotClass(user.status)} mr-1.5"></span>
                ${getStatusLabel(user.status)}
            </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
            ${lastLogin}
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
            <div class="flex justify-end space-x-2">
                <button onclick="editUser('${user._id}')" 
                        class="text-primary-600 hover:text-primary-900 p-1 rounded hover:bg-primary-50"
                        title="Editar usuario">
                    <i class="fas fa-edit"></i>
                </button>
                <button onclick="viewUser('${user._id}')" 
                        class="text-blue-600 hover:text-blue-900 p-1 rounded hover:bg-blue-50"
                        title="Ver detalles">
                    <i class="fas fa-eye"></i>
                </button>
                ${user.role !== 'admin' ? `
                    <button onclick="deleteUser('${user._id}', '${user.first_name} ${user.last_name}')" 
                            class="text-red-600 hover:text-red-900 p-1 rounded hover:bg-red-50"
                            title="Eliminar usuario">
                        <i class="fas fa-trash"></i>
                    </button>
                ` : ''}
            </div>
        </td>
    `;

    return tr;
}

/**
 * Obtener clase CSS para badge de rol
 */
function getRoleBadgeClass(role) {
    const classes = {
        'admin': 'bg-purple-100 text-purple-800',
        'supervisor': 'bg-green-100 text-green-800',
        'contador': 'bg-yellow-100 text-yellow-800',
        'solicitante': 'bg-blue-100 text-blue-800'
    };
    return classes[role] || 'bg-gray-100 text-gray-800';
}

/**
 * Obtener icono para rol
 */
function getRoleIcon(role) {
    const icons = {
        'admin': 'fa-crown',
        'supervisor': 'fa-user-tie',
        'contador': 'fa-calculator',
        'solicitante': 'fa-user'
    };
    return icons[role] || 'fa-user';
}

/**
 * Obtener etiqueta para rol
 */
function getRoleLabel(role) {
    const labels = {
        'admin': 'Administrador',
        'solicitante': 'Solicitante',
        'aprobador': 'Aprobador',
        'pagador': 'Pagador'
    };
    return labels[role] || role;
}

/**
 * Obtener clase CSS para badge de estado
 */
function getStatusBadgeClass(status) {
    const classes = {
        'active': 'bg-green-100 text-green-800',
        'inactive': 'bg-gray-100 text-gray-800',
        'suspended': 'bg-red-100 text-red-800'
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
}

/**
 * Obtener clase CSS para punto de estado
 */
function getStatusDotClass(status) {
    const classes = {
        'active': 'bg-green-400',
        'inactive': 'bg-gray-400',
        'suspended': 'bg-red-400'
    };
    return classes[status] || 'bg-gray-400';
}

/**
 * Obtener etiqueta para estado
 */
function getStatusLabel(status) {
    const labels = {
        'active': 'Activo',
        'inactive': 'Inactivo',
        'suspended': 'Suspendido'
    };
    return labels[status] || status;
}

/**
 * Mostrar estado vacío
 */
function showEmptyState() {
    document.getElementById('loadingUsers').classList.add('hidden');
    document.getElementById('usersTableContainer').classList.add('hidden');
    document.getElementById('emptyState').classList.remove('hidden');
}

/**
 * Actualizar contador de usuarios
 */
function updateUserCount(total) {
    const countElement = document.getElementById('userCount');
    if (countElement) {
        countElement.textContent = `${total} usuario${total !== 1 ? 's' : ''} encontrado${total !== 1 ? 's' : ''}`;
    }
}

/**
 * Actualizar paginación
 */
function updatePagination(pagination) {
    if (!pagination) return;

    totalUsers = pagination.total;
    totalPages = pagination.pages;
    currentPage = pagination.page;

    // Actualizar información de paginación
    const paginationInfo = document.getElementById('paginationInfo');
    if (paginationInfo) {
        const start = (currentPage - 1) * pageSize + 1;
        const end = Math.min(currentPage * pageSize, totalUsers);
        paginationInfo.textContent = `Mostrando ${start} a ${end} de ${totalUsers} resultados`;
    }

    // Actualizar navegación de paginación
    updatePaginationNav();
}

/**
 * Actualizar navegación de paginación
 */
function updatePaginationNav() {
    const nav = document.getElementById('paginationNav');
    if (!nav) return;

    nav.innerHTML = '';

    // Botón anterior
    const prevButton = createPaginationButton('Anterior', currentPage > 1, () => {
        if (currentPage > 1) {
            currentPage--;
            loadUsers();
        }
    });
    nav.appendChild(prevButton);

    // Números de página
    const maxVisible = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);

    if (endPage - startPage + 1 < maxVisible) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
        const pageButton = createPaginationButton(i.toString(), true, () => {
            currentPage = i;
            loadUsers();
        }, i === currentPage);
        nav.appendChild(pageButton);
    }

    // Botón siguiente
    const nextButton = createPaginationButton('Siguiente', currentPage < totalPages, () => {
        if (currentPage < totalPages) {
            currentPage++;
            loadUsers();
        }
    });
    nav.appendChild(nextButton);
}

/**
 * Crear botón de paginación
 */
function createPaginationButton(text, enabled, onClick, active = false) {
    const button = document.createElement('button');
    button.textContent = text;
    button.onclick = enabled ? onClick : null;
    
    let classes = 'relative inline-flex items-center px-4 py-2 border text-sm font-medium ';
    
    if (active) {
        classes += 'z-10 bg-primary-50 border-primary-500 text-primary-600';
    } else if (enabled) {
        classes += 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50';
    } else {
        classes += 'bg-gray-50 border-gray-300 text-gray-300 cursor-not-allowed';
    }
    
    button.className = classes;
    button.disabled = !enabled;
    
    return button;
}

/**
 * Aplicar filtros
 */
function applyFilters() {
    const searchInput = document.getElementById('searchInput');
    const roleFilter = document.getElementById('roleFilter');
    const statusFilter = document.getElementById('statusFilter');

    currentFilters = {};

    if (searchInput?.value.trim()) {
        currentFilters.search = searchInput.value.trim();
    }

    if (roleFilter?.value) {
        currentFilters.role = roleFilter.value;
    }

    if (statusFilter?.value) {
        currentFilters.status = statusFilter.value;
    }

    currentPage = 1; // Resetear a primera página
    loadUsers();
}

/**
 * Limpiar filtros
 */
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('roleFilter').value = '';
    document.getElementById('statusFilter').value = '';
    
    currentFilters = {};
    currentPage = 1;
    loadUsers();
}

/**
 * Refrescar lista de usuarios
 */
function refreshUsers() {
    loadUsers();
    showSuccess('Lista de usuarios actualizada');
}

/**
 * Abrir modal para agregar usuario
 */
function openAddUserModal() {
    editingUserId = null;
    document.getElementById('modalTitle').innerHTML = '<i class="fas fa-user-plus mr-2 text-blue-600"></i>Nuevo Usuario';
    document.getElementById('submitButton').innerHTML = '<i class="fas fa-save mr-2"></i>Guardar';
    
    // Mostrar campo de contraseña para nuevos usuarios
    document.getElementById('passwordField').style.display = 'block';
    document.getElementById('password').required = true;
    
    // Limpiar formulario
    document.getElementById('userForm').reset();
    document.getElementById('userId').value = '';
    
    // Mostrar modal
    document.getElementById('userModal').classList.remove('hidden');
    isModalOpen = true;
    
    // Focus en primer campo
    setTimeout(() => {
        document.getElementById('firstName').focus();
    }, 100);
}

/**
 * Editar usuario
 */
async function editUser(userId) {
    try {
        editingUserId = userId;
        
        // Cargar datos del usuario
        const response = await apiRequest(`/users/${userId}`, {
            method: 'GET'
        });

        if (response) {
            // Actualizar título del modal
            document.getElementById('modalTitle').innerHTML = '<i class="fas fa-user-edit mr-2 text-blue-600"></i>Editar Usuario';
            document.getElementById('submitButton').innerHTML = '<i class="fas fa-save mr-2"></i>Actualizar';
            
            // Ocultar campo de contraseña para edición
            document.getElementById('passwordField').style.display = 'none';
            document.getElementById('password').required = false;
            
            // Llenar formulario con datos
            document.getElementById('userId').value = response._id;
            document.getElementById('firstName').value = response.first_name || '';
            document.getElementById('lastName').value = response.last_name || '';
            document.getElementById('email').value = response.email || '';
            document.getElementById('department').value = response.department || '';
            document.getElementById('phone').value = response.phone || '';
            document.getElementById('role').value = response.role || '';
            document.getElementById('status').value = response.status || '';
            
            // Mostrar modal
            document.getElementById('userModal').classList.remove('hidden');
            isModalOpen = true;
            
            // Focus en primer campo
            setTimeout(() => {
                document.getElementById('firstName').focus();
            }, 100);
        }

    } catch (error) {
        console.error('Error loading user:', error);
        showError('Error al cargar datos del usuario: ' + error.message);
    }
}

/**
 * Ver detalles del usuario
 */
async function viewUser(userId) {
    try {
        const response = await apiRequest(`/users/${userId}`, {
            method: 'GET'
        });

        if (response) {
            // Llenar el modal con la información del usuario
            document.getElementById('detailFullName').textContent = `${response.first_name} ${response.last_name}`;
            document.getElementById('detailEmail').textContent = response.email;
            document.getElementById('detailPhone').textContent = response.phone || 'No registrado';
            document.getElementById('detailDepartment').textContent = response.department || 'No asignado';
            
            // Rol con color
            const roleElement = document.getElementById('detailRole');
            const roleLabel = getRoleLabel(response.role);
            roleElement.textContent = roleLabel;
            roleElement.className = 'font-medium ' + getRoleColor(response.role);
            
            // Estado con color
            const statusElement = document.getElementById('detailStatus');
            const statusLabel = getStatusLabel(response.status);
            statusElement.textContent = statusLabel;
            statusElement.className = 'font-medium ' + getStatusColor(response.status);
            
            // Fechas formateadas
            document.getElementById('detailCreatedAt').textContent = response.created_at ? 
                new Date(response.created_at).toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                }) : 'No disponible';
            
            document.getElementById('detailLastLogin').textContent = response.last_login ? 
                new Date(response.last_login).toLocaleDateString('es-ES', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                }) : 'Nunca';
            
            // Guardar ID para posible edición
            currentDetailUserId = userId;
            
            // Mostrar modal
            document.getElementById('userDetailModal').classList.remove('hidden');
        }

    } catch (error) {
        console.error('Error loading user details:', error);
        showError('Error al cargar detalles del usuario: ' + error.message);
    }
}

/**
 * Manejar envío del formulario
 */
async function handleUserSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const userData = {
        first_name: formData.get('firstName'),
        last_name: formData.get('lastName'),
        email: formData.get('email'),
        department: formData.get('department'),
        phone: formData.get('phone'),
        role: formData.get('role'),
        status: formData.get('status')
    };

    // Agregar contraseña solo si es un nuevo usuario
    if (!editingUserId) {
        userData.password = formData.get('password');
    }

    // Obtener referencia al botón y guardar texto original
    const submitButton = document.getElementById('submitButton');
    const originalText = submitButton.innerHTML;

    try {
        // Mostrar loading en botón
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Guardando...';
        submitButton.disabled = true;

        let response;
        if (editingUserId) {
            // Actualizar usuario existente
            response = await apiRequest(`/users/${editingUserId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });
            showSuccess('Usuario actualizado correctamente');
        } else {
            // Crear nuevo usuario
            response = await apiRequest('/users', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });
            showSuccess('Usuario creado correctamente');
        }

        // Cerrar modal y recargar lista
        closeUserModal();
        loadUsers();

    } catch (error) {
        console.error('Error saving user:', error);
        showError('Error al guardar usuario: ' + error.message);
    } finally {
        // Restaurar botón
        const submitButton = document.getElementById('submitButton');
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    }
}

/**
 * Cerrar modal de usuario
 */
function closeUserModal() {
    document.getElementById('userModal').classList.add('hidden');
    isModalOpen = false;
    editingUserId = null;
    document.getElementById('userForm').reset();
}

/**
 * Eliminar usuario
 */
function deleteUser(userId, userName) {
    deleteUserId = userId;
    document.getElementById('deleteMessage').textContent = 
        `¿Estás seguro de que deseas eliminar al usuario "${userName}"? Esta acción no se puede deshacer.`;
    document.getElementById('deleteModal').classList.remove('hidden');
}

/**
 * Confirmar eliminación de usuario
 */
async function confirmDeleteUser() {
    if (!deleteUserId) return;

    try {
        await apiRequest(`/users/${deleteUserId}`, {
            method: 'DELETE'
        });

        showSuccess('Usuario eliminado correctamente');
        closeDeleteModal();
        loadUsers();

    } catch (error) {
        console.error('Error deleting user:', error);
        showError('Error al eliminar usuario: ' + error.message);
    }
}

/**
 * Cerrar modal de eliminación
 */
function closeDeleteModal() {
    document.getElementById('deleteModal').classList.add('hidden');
    deleteUserId = null;
}

/**
 * Mostrar mensaje de error
 */
function showError(message) {
    showAlert(message, 'error');
}

/**
 * Mostrar mensaje de éxito
 */
function showSuccess(message) {
    showAlert(message, 'success');
}

/**
 * Cerrar modal de detalles
 */
function closeUserDetailModal() {
    document.getElementById('userDetailModal').classList.add('hidden');
    currentDetailUserId = null;
}

/**
 * Editar usuario desde el modal de detalles
 */
function editUserFromDetail() {
    if (currentDetailUserId) {
        closeUserDetailModal();
        editUser(currentDetailUserId);
    }
}

/**
 * Obtener color del rol
 */
function getRoleColor(role) {
    const colors = {
        'admin': 'text-red-600',
        'solicitante': 'text-blue-600',
        'aprobador': 'text-green-600',
        'pagador': 'text-purple-600'
    };
    return colors[role] || 'text-gray-600';
}

/**
 * Obtener color del estado
 */
function getStatusColor(status) {
    const colors = {
        'activo': 'text-green-600',
        'inactivo': 'text-red-600'
    };
    return colors[status] || 'text-gray-600';
}