/**
 * Dashboard de Aprobador - JavaScript Interactivo
 * Sistema EU-UTVT
 * VERSIÓN: 2.0 - Con soporte para Historial
 */

console.log('📄 Archivo aprobador.js cargado - Versión 2.0');

// Variables globales
let solicitudesPendientes = [];
let solicitudesHistorial = [];
let filtrosAplicados = {
    departamento: '',
    tipo_pago: ''
};
let filtrosHistorial = {
    estado: '',
    departamento: '',
    tipo_pago: ''
};
let vistaActual = 'pendientes'; // 'pendientes' o 'historial'

// ========================================
// Inicialización
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando Dashboard de Aprobador - DOMContentLoaded disparado');
    
    // Cargar información del usuario
    cargarInfoUsuario();
    
    // Inicializar eventos inmediatamente
    console.log('⚡ Llamando a inicializarEventos() AHORA...');
    inicializarEventos();
    
    // Luego cargar datos
    cargarEstadisticas();
    cargarSolicitudesPendientes();
    
    // Refrescar cada 2 minutos
    setInterval(() => {
        cargarEstadisticas();
        cargarSolicitudesPendientes();
    }, 120000);
    
    console.log('✅ Inicialización completada');
});

// ========================================
// Información del Usuario
// ========================================
function cargarInfoUsuario() {
    try {
        const userStr = localStorage.getItem('user');
        if (userStr) {
            const user = JSON.parse(userStr);
            const userNameElement = document.getElementById('user-name');
            if (userNameElement && user.nombre) {
                userNameElement.textContent = user.nombre;
            }
        }
    } catch (error) {
        console.error('Error cargando info del usuario:', error);
    }
}

// ========================================
// Event Listeners
// ========================================
function inicializarEventos() {
    console.log('🎯 === INICIALIZANDO EVENTOS ===');
    
    // Pestañas de navegación
    const tabButtons = document.querySelectorAll('.tab-button');
    console.log('🔘 Botones de pestañas encontrados:', tabButtons.length);
    
    if (tabButtons.length === 0) {
        console.error('❌ NO SE ENCONTRARON BOTONES DE PESTAÑAS!');
        console.log('🔍 Intentando buscar por ID...');
        
        // Buscar todo el contenedor de tabs
        const tabsNav = document.querySelector('.tabs-navigation');
        console.log('📦 Contenedor tabs-navigation:', tabsNav);
        
        if (tabsNav) {
            console.log('📝 HTML del contenedor:', tabsNav.innerHTML.substring(0, 200));
        }
    }
    
    tabButtons.forEach((btn, index) => {
        const tabName = btn.getAttribute('data-tab');
        console.log(`  📌 Botón ${index + 1}: data-tab="${tabName}", texto="${btn.textContent.trim()}"`);
        
        // Método 1: addEventListener
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            const tab = this.getAttribute('data-tab');
            console.log('🖱️ CLICK MÉTODO 1 detectado en pestaña:', tab);
            cambiarVista(tab);
        });
        
        // Método 2: onclick directo (backup)
        btn.onclick = function(e) {
            e.preventDefault();
            const tab = this.getAttribute('data-tab');
            console.log('🖱️ CLICK MÉTODO 2 detectado en pestaña:', tab);
            cambiarVista(tab);
        };
    });
    
    console.log('✅ Event listeners de pestañas registrados');
    
    // Botones de filtros - Pendientes
    const btnAplicar = document.getElementById('btn-aplicar-filtros');
    console.log('🔍 btn-aplicar-filtros encontrado:', !!btnAplicar);
    btnAplicar?.addEventListener('click', aplicarFiltros);
    
    document.getElementById('btn-limpiar-filtros')?.addEventListener('click', limpiarFiltros);
    document.getElementById('btn-refrescar')?.addEventListener('click', refrescar);
    
    // Botones de filtros - Historial
    const btnAplicarHist = document.getElementById('btn-aplicar-filtros-historial');
    console.log('🔍 btn-aplicar-filtros-historial encontrado:', !!btnAplicarHist);
    btnAplicarHist?.addEventListener('click', aplicarFiltrosHistorial);
    
    document.getElementById('btn-limpiar-filtros-historial')?.addEventListener('click', limpiarFiltrosHistorial);
    document.getElementById('btn-refrescar-historial')?.addEventListener('click', () => cargarHistorial());
    
    // Modales - Cerrar
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal');
            cerrarModal(modalId);
        });
    });
    
    // Cerrar modal al hacer clic fuera
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                cerrarModal(this.id);
            }
        });
    });
    
    // Botones de confirmación
    document.getElementById('btn-confirmar-aprobar')?.addEventListener('click', confirmarAprobacion);
    document.getElementById('btn-confirmar-rechazar')?.addEventListener('click', confirmarRechazo);
}

// ========================================
// Cargar Datos
// ========================================
async function cargarEstadisticas() {
    try {
        const response = await fetch('/aprobador/api/estadisticas', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (!response.ok) throw new Error('Error al cargar estadísticas');
        
        const data = await response.json();
        const stats = data.estadisticas;
        
        // Actualizar valores
        document.getElementById('stat-pendientes').textContent = stats.pendientes;
        document.getElementById('stat-aprobadas').textContent = stats.aprobadas;
        document.getElementById('stat-rechazadas').textContent = stats.rechazadas;
        document.getElementById('stat-monto').textContent = formatearMoneda(stats.monto_pendiente);
        
    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
        mostrarToast('Error al cargar estadísticas', 'error');
    }
}

async function cargarSolicitudesPendientes() {
    try {
        mostrarCargando();
        
        // Construir URL con filtros
        let url = '/aprobador/api/solicitudes-pendientes?';
        if (filtrosAplicados.departamento) {
            url += `filtro_departamento=${encodeURIComponent(filtrosAplicados.departamento)}&`;
        }
        if (filtrosAplicados.tipo_pago) {
            url += `filtro_tipo_pago=${encodeURIComponent(filtrosAplicados.tipo_pago)}&`;
        }
        
        console.log('🔍 Cargando solicitudes desde:', url);
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        console.log('📡 Response status:', response.status);
        
        if (!response.ok) throw new Error('Error al cargar solicitudes');
        
        const data = await response.json();
        console.log('📦 Datos recibidos:', data);
        console.log('📊 Total solicitudes:', data.total);
        console.log('📋 Solicitudes array:', data.solicitudes);
        
        solicitudesPendientes = data.solicitudes;
        
        renderizarTablaSolicitudes(solicitudesPendientes);
        actualizarContadorSolicitudes(solicitudesPendientes.length);
        
    } catch (error) {
        console.error('❌ Error al cargar solicitudes:', error);
        mostrarToast('Error al cargar solicitudes pendientes', 'error');
        mostrarErrorTabla();
    }
}

// ========================================
// Renderizado
// ========================================
function renderizarTablaSolicitudes(solicitudes) {
    const tbody = document.getElementById('tbody-solicitudes');
    
    if (!solicitudes || solicitudes.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center" style="padding: 40px;">
                    <i class="fas fa-inbox" style="font-size: 3rem; color: #cbd5e1; margin-bottom: 15px;"></i>
                    <p style="font-size: 1.1rem; color: #64748b;">No hay solicitudes pendientes</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = solicitudes.map(solicitud => `
        <tr data-id="${solicitud.id}">
            <td>
                <strong>${solicitud.id.substring(0, 8)}...</strong>
            </td>
            <td>${formatearFecha(solicitud.fecha_creacion)}</td>
            <td>
                <div>
                    <strong>${solicitud.solicitante.nombre}</strong><br>
                    <small class="text-muted">${solicitud.solicitante.email}</small>
                </div>
            </td>
            <td>${solicitud.departamento}</td>
            <td>
                <div>
                    <strong>${solicitud.nombre_beneficiario}</strong><br>
                    <small class="text-muted">${solicitud.nombre_empresa}</small>
                </div>
            </td>
            <td>
                <strong>${formatearMoneda(solicitud.monto)}</strong><br>
                <small class="text-muted">${solicitud.tipo_moneda}</small>
            </td>
            <td>${solicitud.tipo_pago}</td>
            <td>
                <span class="badge badge-${obtenerClaseEstado(solicitud.estado)}">
                    ${solicitud.estado}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button 
                        class="btn btn-info btn-sm" 
                        onclick="verDetalles('${solicitud.id}')"
                        title="Ver detalles">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button 
                        class="btn btn-success btn-sm" 
                        onclick="abrirModalAprobar('${solicitud.id}')"
                        title="Aprobar">
                        <i class="fas fa-check"></i>
                    </button>
                    <button 
                        class="btn btn-danger btn-sm" 
                        onclick="abrirModalRechazar('${solicitud.id}')"
                        title="Rechazar">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function mostrarCargando() {
    const tbody = document.getElementById('tbody-solicitudes');
    tbody.innerHTML = `
        <tr class="loading-row">
            <td colspan="9" class="text-center">
                <div class="loading-spinner">
                    <i class="fas fa-spinner fa-spin"></i>
                    Cargando solicitudes...
                </div>
            </td>
        </tr>
    `;
}

function mostrarErrorTabla() {
    const tbody = document.getElementById('tbody-solicitudes');
    tbody.innerHTML = `
        <tr>
            <td colspan="9" class="text-center" style="padding: 40px;">
                <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: #ef4444; margin-bottom: 15px;"></i>
                <p style="font-size: 1.1rem; color: #64748b;">Error al cargar solicitudes</p>
                <button class="btn btn-primary" onclick="cargarSolicitudesPendientes()">
                    <i class="fas fa-sync-alt"></i> Reintentar
                </button>
            </td>
        </tr>
    `;
}

// ========================================
// Modales
// ========================================
async function verDetalles(solicitudId) {
    try {
        const response = await fetch(`/aprobador/api/solicitud/${solicitudId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (!response.ok) throw new Error('Error al cargar detalles');
        
        const data = await response.json();
        const solicitud = data.solicitud;
        
        // Renderizar detalles
        const detallesHTML = `
            <div class="solicitud-detalles">
                <div class="detalle-section">
                    <h3><i class="fas fa-user"></i> Información del Solicitante</h3>
                    <div class="detalle-grid">
                        <div class="detalle-item">
                            <label>Nombre:</label>
                            <span>${solicitud.solicitante.nombre}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Email:</label>
                            <span>${solicitud.solicitante.email}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Departamento:</label>
                            <span>${solicitud.departamento}</span>
                        </div>
                    </div>
                </div>

                <div class="detalle-section">
                    <h3><i class="fas fa-money-bill"></i> Información del Pago</h3>
                    <div class="detalle-grid">
                        <div class="detalle-item">
                            <label>Monto:</label>
                            <span class="monto-destacado">${formatearMoneda(solicitud.monto)}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Moneda:</label>
                            <span>${solicitud.tipo_moneda}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Tipo de Pago:</label>
                            <span>${solicitud.tipo_pago}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Concepto:</label>
                            <span>${solicitud.concepto_pago}</span>
                        </div>
                    </div>
                </div>

                <div class="detalle-section">
                    <h3><i class="fas fa-building"></i> Información del Beneficiario</h3>
                    <div class="detalle-grid">
                        <div class="detalle-item">
                            <label>Nombre:</label>
                            <span>${solicitud.nombre_beneficiario}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Empresa:</label>
                            <span>${solicitud.nombre_empresa}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Banco:</label>
                            <span>${solicitud.banco_destino}</span>
                        </div>
                        <div class="detalle-item">
                            <label>Cuenta:</label>
                            <span>${solicitud.cuenta_destino}</span>
                        </div>
                    </div>
                </div>

                <div class="detalle-section">
                    <h3><i class="fas fa-file-alt"></i> Descripción</h3>
                    <p>${solicitud.descripcion_tipo_pago}</p>
                </div>

                ${solicitud.comentarios_solicitante ? `
                    <div class="detalle-section">
                        <h3><i class="fas fa-comment"></i> Comentarios del Solicitante</h3>
                        <p>${solicitud.comentarios_solicitante}</p>
                    </div>
                ` : ''}

                ${solicitud.archivos_adjuntos && solicitud.archivos_adjuntos.length > 0 ? `
                    <div class="detalle-section">
                        <h3><i class="fas fa-paperclip"></i> Archivos Adjuntos (${solicitud.archivos_adjuntos.length})</h3>
                        <div class="archivos-grid">
                            ${solicitud.archivos_adjuntos.map(archivo => {
                                // Construir la ruta completa del archivo
                                let rutaCompleta = '';
                                if (archivo.ruta) {
                                    rutaCompleta = archivo.ruta;
                                } else if (archivo.ruta_archivo) {
                                    // Si solo tiene el nombre del archivo, construir la ruta
                                    rutaCompleta = `/uploads/solicitudes/${archivo.ruta_archivo}`;
                                } else {
                                    rutaCompleta = '#';
                                }
                                
                                const nombreArchivo = archivo.nombre_archivo || archivo.nombre || 'Archivo sin nombre';
                                const extension = nombreArchivo.split('.').pop().toLowerCase();
                                const esImagen = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(extension);
                                const esPDF = extension === 'pdf';
                                const esExcel = ['xls', 'xlsx', 'csv'].includes(extension);
                                const esWord = ['doc', 'docx'].includes(extension);
                                
                                let icono = 'fa-file';
                                let colorIcono = '#64748b';
                                
                                if (esImagen) {
                                    icono = 'fa-file-image';
                                    colorIcono = '#10b981';
                                } else if (esPDF) {
                                    icono = 'fa-file-pdf';
                                    colorIcono = '#ef4444';
                                } else if (esExcel) {
                                    icono = 'fa-file-excel';
                                    colorIcono = '#10b981';
                                } else if (esWord) {
                                    icono = 'fa-file-word';
                                    colorIcono = '#3b82f6';
                                }
                                
                                console.log('📎 Archivo:', {nombre: nombreArchivo, ruta: rutaCompleta, extension});
                                
                                return `
                                    <div class="archivo-card" style="cursor: pointer;" data-ruta="${rutaCompleta}" data-nombre="${nombreArchivo}" data-ext="${extension}">
                                        <div class="archivo-preview">
                                            ${esImagen && rutaCompleta !== '#' ? 
                                                `<img src="${rutaCompleta}" alt="${nombreArchivo}" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                                                <div class="archivo-icon" style="display:none;">
                                                    <i class="fas ${icono}" style="color: ${colorIcono};"></i>
                                                </div>` :
                                                `<div class="archivo-icon">
                                                    <i class="fas ${icono}" style="color: ${colorIcono};"></i>
                                                </div>`
                                            }
                                        </div>
                                        <div class="archivo-info">
                                            <div class="archivo-nombre" title="${nombreArchivo}">${nombreArchivo}</div>
                                            <div class="archivo-detalles">
                                                <span class="archivo-extension">${extension.toUpperCase()}</span>
                                                ${archivo.tamaño ? `<span class="archivo-tamaño">${formatearTamaño(archivo.tamaño)}</span>` : ''}
                                            </div>
                                        </div>
                                        <div class="archivo-acciones">
                                            <button class="btn-archivo btn-descargar-archivo" data-ruta="${rutaCompleta}" data-nombre="${nombreArchivo}" title="Descargar">
                                                <i class="fas fa-download"></i>
                                            </button>
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>

            <style>
                .solicitud-detalles {
                    padding: 10px;
                }
                .detalle-section {
                    margin-bottom: 25px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid #e2e8f0;
                }
                .detalle-section:last-child {
                    border-bottom: none;
                }
                .detalle-section h3 {
                    color: #1e293b;
                    margin-bottom: 15px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .detalle-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 15px;
                }
                .detalle-item {
                    display: flex;
                    flex-direction: column;
                    gap: 5px;
                }
                .detalle-item label {
                    font-weight: 600;
                    color: #64748b;
                    font-size: 0.85rem;
                }
                .detalle-item span {
                    color: #1e293b;
                    font-size: 0.95rem;
                }
                .monto-destacado {
                    font-size: 1.5rem !important;
                    font-weight: 700 !important;
                    color: #10b981 !important;
                }
                .archivos-lista {
                    list-style: none;
                    padding: 0;
                }
                .archivos-lista li {
                    padding: 10px;
                    background: #f8fafc;
                    margin-bottom: 8px;
                    border-radius: 6px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
            </style>
        `;
        
        document.getElementById('detalles-content').innerHTML = detallesHTML;
        
        // Agregar event listeners para las tarjetas de archivos
        setTimeout(() => {
            // Listeners para las tarjetas (previsualizar)
            document.querySelectorAll('.archivo-card').forEach(card => {
                card.addEventListener('click', function() {
                    const ruta = this.getAttribute('data-ruta');
                    const nombre = this.getAttribute('data-nombre');
                    const ext = this.getAttribute('data-ext');
                    console.log('🖱️ Click en archivo:', {ruta, nombre, ext});
                    previewArchivo(ruta, nombre, ext);
                });
            });
            
            // Listeners para los botones de descarga
            document.querySelectorAll('.btn-descargar-archivo').forEach(btn => {
                btn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const ruta = this.getAttribute('data-ruta');
                    const nombre = this.getAttribute('data-nombre');
                    console.log('📥 Click en descargar:', {ruta, nombre});
                    descargarArchivo(ruta, nombre);
                });
            });
        }, 100);
        
        abrirModal('modal-detalles');
        
    } catch (error) {
        console.error('Error al cargar detalles:', error);
        mostrarToast('Error al cargar los detalles de la solicitud', 'error');
    }
}

function abrirModalAprobar(solicitudId) {
    const solicitud = solicitudesPendientes.find(s => s.id === solicitudId);
    if (!solicitud) return;
    
    document.getElementById('aprobar-solicitud-id').value = solicitudId;
    document.getElementById('aprobar-solicitud-info').innerHTML = `
        <strong>ID:</strong> ${solicitudId.substring(0, 8)}... | 
        <strong>Beneficiario:</strong> ${solicitud.nombre_beneficiario} | 
        <strong>Monto:</strong> ${formatearMoneda(solicitud.monto)}
    `;
    document.getElementById('aprobar-comentarios').value = '';
    
    abrirModal('modal-aprobar');
}

function abrirModalRechazar(solicitudId) {
    const solicitud = solicitudesPendientes.find(s => s.id === solicitudId);
    if (!solicitud) return;
    
    document.getElementById('rechazar-solicitud-id').value = solicitudId;
    document.getElementById('rechazar-solicitud-info').innerHTML = `
        <strong>ID:</strong> ${solicitudId.substring(0, 8)}... | 
        <strong>Beneficiario:</strong> ${solicitud.nombre_beneficiario} | 
        <strong>Monto:</strong> ${formatearMoneda(solicitud.monto)}
    `;
    document.getElementById('rechazar-comentarios').value = '';
    
    abrirModal('modal-rechazar');
}

function abrirModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

function cerrarModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
}

// ========================================
// Acciones de Aprobación/Rechazo
// ========================================
async function confirmarAprobacion() {
    const solicitudId = document.getElementById('aprobar-solicitud-id').value;
    const comentarios = document.getElementById('aprobar-comentarios').value;
    
    if (!solicitudId) {
        mostrarToast('Error: ID de solicitud no válido', 'error');
        return;
    }
    
    const btnConfirmar = document.getElementById('btn-confirmar-aprobar');
    btnConfirmar.disabled = true;
    btnConfirmar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
    
    try {
        const requestData = {
            solicitud_id: solicitudId
        };
        
        // Solo incluir comentarios si hay alguno
        if (comentarios && comentarios.trim()) {
            requestData.comentarios_aprobador = comentarios.trim();
        }
        
        console.log('📤 Enviando aprobación:', requestData);
        
        const response = await fetch('/aprobador/api/aprobar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            console.error('❌ Error en respuesta:', data);
            throw new Error(data.detail || 'Error al aprobar solicitud');
        }
        
        // Éxito
        mostrarToast('✅ Solicitud aprobada exitosamente', 'success');
        cerrarModal('modal-aprobar');
        
        // Refrescar datos
        await cargarEstadisticas();
        await cargarSolicitudesPendientes();
        
    } catch (error) {
        console.error('Error al aprobar:', error);
        mostrarToast(`Error: ${error.message}`, 'error');
    } finally {
        btnConfirmar.disabled = false;
        btnConfirmar.innerHTML = '<i class="fas fa-check"></i> Aprobar Solicitud';
    }
}

async function confirmarRechazo() {
    const solicitudId = document.getElementById('rechazar-solicitud-id').value;
    const comentarios = document.getElementById('rechazar-comentarios').value.trim();
    
    if (!solicitudId) {
        mostrarToast('Error: ID de solicitud no válido', 'error');
        return;
    }
    
    if (!comentarios || comentarios.length < 10) {
        mostrarToast('Debe proporcionar un comentario detallado (mínimo 10 caracteres)', 'warning');
        document.getElementById('rechazar-comentarios').focus();
        return;
    }
    
    const btnConfirmar = document.getElementById('btn-confirmar-rechazar');
    btnConfirmar.disabled = true;
    btnConfirmar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
    
    try {
        const requestData = {
            solicitud_id: solicitudId,
            comentarios_aprobador: comentarios
        };
        
        console.log('📤 Enviando rechazo:', requestData);
        
        const response = await fetch('/aprobador/api/rechazar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            console.error('❌ Error en respuesta:', data);
            throw new Error(data.detail || 'Error al rechazar solicitud');
        }
        
        // Éxito
        mostrarToast('✅ Solicitud rechazada exitosamente', 'success');
        cerrarModal('modal-rechazar');
        
        // Refrescar datos
        await cargarEstadisticas();
        await cargarSolicitudesPendientes();
        
    } catch (error) {
        console.error('Error al rechazar:', error);
        mostrarToast(`Error: ${error.message}`, 'error');
    } finally {
        btnConfirmar.disabled = false;
        btnConfirmar.innerHTML = '<i class="fas fa-ban"></i> Rechazar Solicitud';
    }
}

// ========================================
// Filtros
// ========================================
function aplicarFiltros() {
    filtrosAplicados.departamento = document.getElementById('filter-departamento').value;
    filtrosAplicados.tipo_pago = document.getElementById('filter-tipo-pago').value;
    
    cargarSolicitudesPendientes();
    mostrarToast('Filtros aplicados', 'info');
}

function limpiarFiltros() {
    document.getElementById('filter-departamento').value = '';
    document.getElementById('filter-tipo-pago').value = '';
    
    filtrosAplicados = {
        departamento: '',
        tipo_pago: ''
    };
    
    cargarSolicitudesPendientes();
    mostrarToast('Filtros limpiados', 'info');
}

function refrescar() {
    const btn = document.getElementById('btn-refrescar');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refrescando...';
    btn.disabled = true;
    
    Promise.all([
        cargarEstadisticas(),
        cargarSolicitudesPendientes()
    ]).then(() => {
        btn.innerHTML = '<i class="fas fa-sync-alt"></i> Refrescar';
        btn.disabled = false;
        mostrarToast('Datos actualizados', 'success');
    }).catch(() => {
        btn.innerHTML = '<i class="fas fa-sync-alt"></i> Refrescar';
        btn.disabled = false;
    });
}

// ========================================
// Utilidades
// ========================================
function formatearMoneda(monto) {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: 'MXN'
    }).format(monto);
}

function formatearFecha(fecha) {
    if (!fecha) return 'N/A';
    const date = new Date(fecha);
    return date.toLocaleDateString('es-MX', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatearTamaño(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function obtenerClaseEstado(estado) {
    const clases = {
        'enviada': 'enviada',
        'en_revision': 'en-revision',
        'aprobada': 'aprobada',
        'rechazada': 'rechazada'
    };
    return clases[estado] || 'default';
}

// ========================================
// Funciones para Archivos
// ========================================
function previewArchivo(ruta, nombre, extension) {
    if (!ruta || ruta === '#') {
        mostrarToast('Archivo no disponible para previsualización', 'warning');
        return;
    }
    
    const esImagen = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(extension);
    const esPDF = extension === 'pdf';
    
    if (esImagen || esPDF) {
        // Crear modal de previsualización
        const modalPreview = document.createElement('div');
        modalPreview.className = 'modal modal-preview active';
        modalPreview.innerHTML = `
            <div class="modal-overlay" onclick="cerrarPreview()"></div>
            <div class="modal-content modal-preview-content">
                <div class="modal-header">
                    <h2>
                        <i class="fas fa-eye"></i>
                        ${nombre}
                    </h2>
                    <button class="modal-close" onclick="cerrarPreview()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body modal-preview-body">
                    ${esImagen ? 
                        `<img src="${ruta}" alt="${nombre}" style="max-width: 100%; max-height: 80vh; object-fit: contain;">` :
                        `<iframe src="${ruta}" style="width: 100%; height: 80vh; border: none;"></iframe>`
                    }
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="cerrarPreview()">
                        <i class="fas fa-times"></i> Cerrar
                    </button>
                    <button class="btn btn-primary" onclick="descargarArchivo('${ruta}', '${nombre}')">
                        <i class="fas fa-download"></i> Descargar
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modalPreview);
    } else {
        // Para otros tipos de archivo, descargar directamente
        descargarArchivo(ruta, nombre);
    }
}

function cerrarPreview() {
    const modal = document.querySelector('.modal-preview');
    if (modal) {
        modal.remove();
    }
}

function descargarArchivo(ruta, nombre) {
    if (!ruta || ruta === '#') {
        mostrarToast('Archivo no disponible para descarga', 'error');
        return;
    }
    
    const link = document.createElement('a');
    link.href = ruta;
    link.download = nombre;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    mostrarToast('Descargando archivo...', 'info');
}

function actualizarContadorSolicitudes(total) {
    const elemento = document.getElementById('total-solicitudes');
    if (elemento) {
        elemento.textContent = `${total} solicitud${total !== 1 ? 'es' : ''}`;
    }
}

function actualizarContadorHistorial(total) {
    const elemento = document.getElementById('total-historial');
    if (elemento) {
        elemento.textContent = `${total} solicitud${total !== 1 ? 'es' : ''}`;
    }
}

// ========================================
// Navegación entre Vistas
// ========================================
function cambiarVista(vista) {
    console.log('🔀 Cambiando vista a:', vista);
    vistaActual = vista;
    
    // Actualizar pestañas activas
    document.querySelectorAll('.tab-button').forEach(btn => {
        const btnTab = btn.getAttribute('data-tab');
        if (btnTab === vista) {
            btn.classList.add('active');
            console.log('✅ Tab activo:', btnTab);
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Obtener elementos
    const filtrosPendientes = document.getElementById('filtros-pendientes');
    const filtrosHistorial = document.getElementById('filtros-historial');
    const seccionPendientes = document.getElementById('seccion-pendientes');
    const seccionHistorial = document.getElementById('seccion-historial');
    
    console.log('📋 Elementos encontrados:', {
        filtrosPendientes: !!filtrosPendientes,
        filtrosHistorial: !!filtrosHistorial,
        seccionPendientes: !!seccionPendientes,
        seccionHistorial: !!seccionHistorial
    });
    
    // Mostrar/ocultar según la vista
    if (vista === 'pendientes') {
        console.log('👁️ Mostrando vista PENDIENTES');
        if (filtrosPendientes) filtrosPendientes.style.display = 'flex';
        if (filtrosHistorial) filtrosHistorial.style.display = 'none';
        if (seccionPendientes) seccionPendientes.style.display = 'block';
        if (seccionHistorial) seccionHistorial.style.display = 'none';
    } else if (vista === 'historial') {
        console.log('👁️ Mostrando vista HISTORIAL');
        if (filtrosPendientes) filtrosPendientes.style.display = 'none';
        if (filtrosHistorial) filtrosHistorial.style.display = 'flex';
        if (seccionPendientes) seccionPendientes.style.display = 'none';
        if (seccionHistorial) seccionHistorial.style.display = 'block';
        
        // Cargar historial si no está cargado
        console.log('📊 Solicitudes en historial:', solicitudesHistorial.length);
        if (solicitudesHistorial.length === 0) {
            console.log('🔄 Cargando historial por primera vez...');
            cargarHistorial();
        }
    }
}

// ========================================
// Cargar Historial
// ========================================
async function cargarHistorial() {
    try {
        console.log('📜 Cargando historial...');
        
        const tbody = document.getElementById('tbody-historial');
        tbody.innerHTML = `
            <tr class="loading-row">
                <td colspan="9" class="text-center">
                    <div class="loading-spinner">
                        <i class="fas fa-spinner fa-spin"></i>
                        Cargando historial...
                    </div>
                </td>
            </tr>
        `;
        
        // Construir URL con filtros
        let url = '/aprobador/api/historial?';
        if (filtrosHistorial.estado) {
            url += `filtro_estado=${encodeURIComponent(filtrosHistorial.estado)}&`;
        }
        if (filtrosHistorial.departamento) {
            url += `filtro_departamento=${encodeURIComponent(filtrosHistorial.departamento)}&`;
        }
        if (filtrosHistorial.tipo_pago) {
            url += `filtro_tipo_pago=${encodeURIComponent(filtrosHistorial.tipo_pago)}&`;
        }
        
        console.log('🔍 URL:', url);
        
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (!response.ok) throw new Error('Error al cargar historial');
        
        const data = await response.json();
        console.log('📊 Historial recibido:', data);
        
        solicitudesHistorial = data.solicitudes || [];
        renderizarTablaHistorial(solicitudesHistorial);
        actualizarContadorHistorial(solicitudesHistorial.length);
        
    } catch (error) {
        console.error('❌ Error al cargar historial:', error);
        mostrarToast('Error al cargar historial', 'error');
        const tbody = document.getElementById('tbody-historial');
        tbody.innerHTML = `
            <tr class="error-row">
                <td colspan="9" class="text-center">
                    <div class="error-message">
                        <i class="fas fa-exclamation-triangle"></i>
                        Error al cargar historial
                    </div>
                </td>
            </tr>
        `;
    }
}

// ========================================
// Renderizar Tabla Historial
// ========================================
function renderizarTablaHistorial(solicitudes) {
    const tbody = document.getElementById('tbody-historial');
    
    if (!solicitudes || solicitudes.length === 0) {
        tbody.innerHTML = `
            <tr class="empty-row">
                <td colspan="9" class="text-center">
                    <div class="empty-message">
                        <i class="fas fa-inbox"></i>
                        No hay solicitudes en el historial
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = '';
    
    solicitudes.forEach(sol => {
        const estadoClass = obtenerClaseEstado(sol.estado);
        const estadoTexto = sol.estado.charAt(0).toUpperCase() + sol.estado.slice(1).replace('_', ' ');
        const fechaProcesada = sol.fecha_aprobacion ? formatearFecha(sol.fecha_aprobacion) : 'N/A';
        const solicitanteNombre = sol.solicitante?.nombre || 'N/A';
        const solicitanteEmail = sol.solicitante?.email || 'N/A';
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${sol.folio || 'N/A'}</strong></td>
            <td>${fechaProcesada}</td>
            <td>
                <div>${solicitanteNombre}</div>
                <small style="color: #64748b;">${solicitanteEmail}</small>
            </td>
            <td>${sol.departamento || 'N/A'}</td>
            <td>
                <div>${sol.nombre_beneficiario || 'N/A'}</div>
                <small style="color: #64748b;">${sol.banco_destino || 'N/A'}</small>
            </td>
            <td>
                <strong>${formatearMoneda(sol.monto || 0)}</strong>
                <br><small style="color: #64748b;">${sol.tipo_moneda || 'MXN'}</small>
            </td>
            <td>${sol.tipo_pago || 'N/A'}</td>
            <td>
                <span class="badge badge-${estadoClass}">${estadoTexto}</span>
                ${sol.estado === 'pagada' ? '<br><small style="color: #8b5cf6;">✓ Pagada</small>' : ''}
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-sm btn-info" onclick="verDetalles('${sol.id}')">
                        <i class="fas fa-eye"></i> Ver
                    </button>
                </div>
            </td>
        `;
        
        tbody.appendChild(tr);
    });
}

// ========================================
// Filtros de Historial
// ========================================
function aplicarFiltrosHistorial() {
    filtrosHistorial = {
        estado: document.getElementById('filter-historial-estado').value,
        departamento: document.getElementById('filter-historial-departamento').value,
        tipo_pago: document.getElementById('filter-historial-tipo-pago').value
    };
    
    console.log('🔍 Aplicando filtros al historial:', filtrosHistorial);
    cargarHistorial();
}

function limpiarFiltrosHistorial() {
    document.getElementById('filter-historial-estado').value = '';
    document.getElementById('filter-historial-departamento').value = '';
    document.getElementById('filter-historial-tipo-pago').value = '';
    
    filtrosHistorial = {
        estado: '',
        departamento: '',
        tipo_pago: ''
    };
    
    console.log('🧹 Filtros de historial limpiados');
    cargarHistorial();
}

// ========================================
// Toast Notifications
// ========================================
function mostrarToast(mensaje, tipo = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const iconos = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${tipo}`;
    toast.innerHTML = `
        <i class="fas ${iconos[tipo]}"></i>
        <span class="toast-message">${mensaje}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(toast);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// ========================================
// Exponer funciones globalmente para onclick
// ========================================
window.cambiarVista = cambiarVista;
window.verDetalles = verDetalles;
window.abrirModalAprobar = abrirModalAprobar;
window.abrirModalRechazar = abrirModalRechazar;
window.previewArchivo = previewArchivo;
window.descargarArchivo = descargarArchivo;
window.cerrarPreview = cerrarPreview;

console.log('✅ Dashboard de Aprobador cargado correctamente - Versión 2.0 con Historial');
