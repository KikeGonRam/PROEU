// Autenticación y gestión de sesiones

// Variables globales para autenticación
let isAuthenticated = false;
let currentUser = null;
let authToken = null;

// Hacer variables accesibles globalmente
window.authToken = authToken;
window.currentUser = currentUser;
window.isAuthenticated = isAuthenticated;

// Verificar autenticación al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    checkAuthentication();
    setupAuthEvents();
});

// Verificar si el usuario está autenticado
function checkAuthentication() {
    const token = localStorage.getItem('authToken');
    const userData = localStorage.getItem('userData');
    
    if (token && userData) {
        authToken = token;
        window.authToken = token;
        currentUser = JSON.parse(userData);
        window.currentUser = currentUser;
        isAuthenticated = true;
        window.isAuthenticated = true;
        updateUIForAuthenticatedUser();
    } else {
        isAuthenticated = false;
        window.isAuthenticated = false;
        updateUIForUnauthenticatedUser();
    }
}

// Configurar eventos de autenticación
function setupAuthEvents() {
    // Formulario de login
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Formulario de registro
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // Botón de logout
    const logoutButtons = document.querySelectorAll('[onclick="logout()"]');
    logoutButtons.forEach(button => {
        button.addEventListener('click', logout);
    });
}

// Manejar login
async function handleLogin(event) {
    event.preventDefault();
    
    const loginButton = document.getElementById('loginButton');
    const loginButtonText = document.getElementById('loginButtonText');
    const originalText = loginButtonText.textContent;
    
    try {
        // Mostrar loading
        loginButton.disabled = true;
        loginButtonText.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Iniciando sesión...';
        
        // Obtener datos del formulario
        const formData = new FormData(event.target);
        const loginData = {
            email: formData.get('email'),
            password: formData.get('password')
        };
        
        // Realizar login
        const response = await apiRequest('/users/login', {
            method: 'POST',
            body: JSON.stringify(loginData)
        });
        
        // Guardar token y datos del usuario
        localStorage.setItem('authToken', response.access_token);
        localStorage.setItem('userData', JSON.stringify(response.user));
        
        // Actualizar variables globales
        authToken = response.access_token;
        window.authToken = response.access_token;
        currentUser = response.user;
        window.currentUser = response.user;
        isAuthenticated = true;
        window.isAuthenticated = true;
        
        // Mostrar mensaje de éxito
        showAlert(`¡Bienvenido, ${response.user.first_name}!`, 'success');
        
        // Redirigir al dashboard
        setTimeout(() => {
            window.location.href = '/home';
        }, 1000);
        
    } catch (error) {
        console.error('Error en login:', error);
        showAlert('Error al iniciar sesión: ' + error.message, 'error');
        
        // Restaurar botón
        loginButton.disabled = false;
        loginButtonText.textContent = originalText;
    }
}

// Manejar registro
async function handleRegister(event) {
    event.preventDefault();
    
    const registerButton = document.getElementById('registerButton');
    const registerButtonText = document.getElementById('registerButtonText');
    const originalText = registerButtonText.textContent;
    
    try {
        // Validar formulario
        if (!validateRegisterForm()) {
            return;
        }
        
        // Mostrar loading
        registerButton.disabled = true;
        registerButtonText.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Creando cuenta...';
        
        // Obtener datos del formulario
        const formData = new FormData(event.target);
        const registerData = {
            email: formData.get('email'),
            password: formData.get('password'),
            first_name: formData.get('firstName'),
            last_name: formData.get('lastName'),
            department: formData.get('department'),
            phone: formData.get('phone') || null,
            role: 'solicitante', // Por defecto, todos los registros son solicitantes
            status: 'active'
        };
        
        // Realizar registro
        const response = await apiRequest('/users/register', {
            method: 'POST',
            body: JSON.stringify(registerData)
        });
        
        // Mostrar mensaje de éxito
        showAlert('¡Cuenta creada exitosamente! Puedes iniciar sesión ahora.', 'success');
        
        // Redirigir al login después de un momento
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
        
    } catch (error) {
        console.error('Error en registro:', error);
        showAlert('Error al crear cuenta: ' + error.message, 'error');
        
        // Restaurar botón
        registerButton.disabled = false;
        registerButtonText.textContent = originalText;
    }
}

// Validar formulario de registro
function validateRegisterForm() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const terms = document.getElementById('terms').checked;
    
    // Verificar que las contraseñas coincidan
    if (password !== confirmPassword) {
        showAlert('Las contraseñas no coinciden', 'error');
        return false;
    }
    
    // Verificar longitud mínima de contraseña
    if (password.length < 6) {
        showAlert('La contraseña debe tener al menos 6 caracteres', 'error');
        return false;
    }
    
    // Verificar términos y condiciones
    if (!terms) {
        showAlert('Debes aceptar los términos y condiciones', 'error');
        return false;
    }
    
    return true;
}

// Cerrar sesión
function logout() {
    // Limpiar localStorage
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
    
    // Limpiar variables globales
    authToken = null;
    window.authToken = null;
    currentUser = null;
    window.currentUser = null;
    isAuthenticated = false;
    window.isAuthenticated = false;
    
    // Mostrar mensaje
    showAlert('Sesión cerrada exitosamente', 'success');
    
    // Redirigir al login
    setTimeout(() => {
        window.location.href = '/login';
    }, 1000);
}

// Actualizar UI para usuario autenticado
function updateUIForAuthenticatedUser() {
    // Ocultar elementos para usuarios no autenticados
    const unauthElements = document.querySelectorAll('.unauth-only');
    unauthElements.forEach(element => {
        element.style.display = 'none';
    });
    
    // Mostrar elementos para usuarios autenticados
    const authElements = document.querySelectorAll('.auth-only');
    authElements.forEach(element => {
        element.style.display = 'block';
    });
    
    // Actualizar información del usuario en el header
    updateUserInfo();
}

// Actualizar UI para usuario no autenticado
function updateUIForUnauthenticatedUser() {
    // Mostrar elementos para usuarios no autenticados
    const unauthElements = document.querySelectorAll('.unauth-only');
    unauthElements.forEach(element => {
        element.style.display = 'block';
    });
    
    // Ocultar elementos para usuarios autenticados
    const authElements = document.querySelectorAll('.auth-only');
    authElements.forEach(element => {
        element.style.display = 'none';
    });
}

// Actualizar información del usuario
function updateUserInfo() {
    if (!currentUser) return;
    
    // Actualizar nombre en el header
    const userNameElements = document.querySelectorAll('.user-name');
    userNameElements.forEach(element => {
        element.textContent = `${currentUser.first_name} ${currentUser.last_name}`;
    });
    
    // Actualizar email
    const userEmailElements = document.querySelectorAll('.user-email');
    userEmailElements.forEach(element => {
        element.textContent = currentUser.email;
    });
    
    // Actualizar departamento
    const userDepartmentElements = document.querySelectorAll('.user-department');
    userDepartmentElements.forEach(element => {
        element.textContent = currentUser.department;
    });
    
    // Actualizar rol
    const userRoleElements = document.querySelectorAll('.user-role');
    userRoleElements.forEach(element => {
        element.textContent = currentUser.role === 'admin' ? 'Administrador' : 'Solicitante';
    });
    
    // Mostrar/ocultar elementos según el rol
    if (currentUser.role === 'admin') {
        document.querySelectorAll('.admin-only').forEach(element => {
            element.style.display = 'block';
        });
    } else {
        document.querySelectorAll('.admin-only').forEach(element => {
            element.style.display = 'none';
        });
    }
}

// Verificar si el usuario tiene permiso de administrador
function isAdmin() {
    return currentUser && currentUser.role === 'admin';
}

// Verificar si el usuario está autenticado
function requireAuth() {
    if (!isAuthenticated) {
        showAlert('Debes iniciar sesión para acceder a esta función', 'warning');
        window.location.href = '/login';
        return false;
    }
    return true;
}

// Verificar si el usuario es administrador
function requireAdmin() {
    if (!requireAuth()) return false;
    
    if (!isAdmin()) {
        showAlert('No tienes permisos de administrador para esta función', 'error');
        return false;
    }
    return true;
}

// Interceptor para peticiones API que requieren autenticación
const originalApiRequest = window.apiRequest;
window.apiRequest = async function(url, options = {}) {
    // Si no hay token y la URL requiere autenticación, redirigir al login
    if (!authToken && url !== '/users/login' && url !== '/users/register') {
        if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
            showAlert('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.', 'warning');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
            throw new Error('Sesión expirada');
        }
    }
    
    try {
        return await originalApiRequest(url, options);
    } catch (error) {
        // Si el error es 401 (no autorizado), redirigir al login
        if (error.message.includes('401') || error.message.includes('Unauthorized')) {
            logout();
            throw new Error('Sesión expirada');
        }
        throw error;
    }
};

// Funciones de utilidad para el frontend
function getAuthHeaders() {
    return authToken ? { 'Authorization': `Bearer ${authToken}` } : {};
}

function getCurrentUser() {
    return currentUser;
}

function isLoggedIn() {
    return isAuthenticated;
}