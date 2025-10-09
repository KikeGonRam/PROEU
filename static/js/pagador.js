/**
 * Dashboard de Pagador - JavaScript Interactivo
 * Sistema EU-UTVT
 */

// Variables globales
let solicitudesAprobadas = [];
let filtrosAplicados = {
    departamento: '',
    tipo_pago: ''
};
let archivosSeleccionados = [];

// ========================================
// Inicialización
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando Dashboard de Pagador');
    
    // Cargar información del usuario
    cargarInfoUsuario();
    
    inicializarEventos();
    cargarEstadisticas();
    cargarSolicitudesAprobadas();
    
    // Refrescar cada 2 minutos
    setInterval(() => {
        cargarEstadisticas();
        cargarSolicitudesAprobadas();
    }, 120000);
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
    // Botones de filtros
    document.getElementById('btn-aplicar-filtros')?.addEventListener('click', aplicarFiltros);
    document.getElementById('btn-limpiar-filtros')?.addEventListener('click', limpiarFiltros);
    document.getElementById('btn-refrescar')?.addEventListener('click', refrescar);
    
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
    document.getElementById('btn-confirmar-pagar')?.addEventListener('click', confirmarPago);
    document.getElementById('btn-subir-comprobantes')?.addEventListener('click', subirComprobantes);
    
    // Upload de archivos
    inicializarUpload();
}

// ========================================
// Cargar Datos
// ========================================
async function cargarEstadisticas() {
    try {
        const response = await fetch('/pagador/api/estadisticas', {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (!response.ok) throw new Error('Error al cargar estadísticas');
        
        const data = await response.json();
        const stats = data.estadisticas;
        
        // Actualizar valores
        document.getElementById('stat-pendientes').textContent = stats.pendientes_pago;
        document.getElementById('stat-pagadas').textContent = stats.pagadas_mes;
        document.getElementById('stat-comprobantes').textContent = stats.comprobantes_pendientes;
        document.getElementById('stat-monto').textContent = formatearMoneda(stats.monto_pagado_mes);
        
    } catch (error) {
        console.error('Error al cargar estadísticas:', error);
        mostrarToast('Error al cargar estadísticas', 'error');
    }
}

async function cargarSolicitudesAprobadas() {
    try {
        mostrarCargando();
        
        // Construir URL con filtros
        let url = '/pagador/api/solicitudes-aprobadas?';
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
        
        solicitudesAprobadas = data.solicitudes;
        
        renderizarTablaSolicitudes(solicitudesAprobadas);
        actualizarContadorSolicitudes(solicitudesAprobadas.length);
        
    } catch (error) {
        console.error('❌ Error al cargar solicitudes:', error);
        mostrarToast('Error al cargar solicitudes aprobadas', 'error');
        mostrarErrorTabla();
    }
}

// ========================================
// Renderizado de Tabla
// ========================================
function renderizarTablaSolicitudes(solicitudes) {
    const container = document.getElementById('tabla-solicitudes-container');
    
    if (!solicitudes || solicitudes.length === 0) {
        container.innerHTML = `
            <div class="loading-spinner">
                <i class="fas fa-inbox"></i>
                <p>No hay solicitudes aprobadas pendientes de pago</p>
            </div>
        `;
        return;
    }
    
    let html = `
        <table class="solicitudes-table">
            <thead>
                <tr>
                    <th>Folio</th>
                    <th>Solicitante</th>
                    <th>Departamento</th>
                    <th>Tipo de Pago</th>
                    <th>Beneficiario</th>
                    <th>Monto</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    solicitudes.forEach(sol => {
        const estadoClass = obtenerClaseEstado(sol.estado);
        const estadoTexto = sol.estado.charAt(0).toUpperCase() + sol.estado.slice(1).replace('_', ' ');
        
        // Generar folio si no existe
        const folio = sol.folio || `SOL-${sol.id?.substring(0, 8).toUpperCase() || 'XXXXX'}`;
        
        // Datos del solicitante
        const solicitanteEmail = sol.solicitante_email || 'N/A';
        const solicitanteDept = sol.departamento || 'N/A';
        
        // Información del beneficiario
        const beneficiarioNombre = sol.nombre_beneficiario || 'N/A';
        const bancoDestino = sol.banco_destino || 'N/A';
        
        // Monto y moneda
        const monto = sol.monto || 0;
        const moneda = sol.tipo_moneda || 'MXN';
        
        html += `
            <tr>
                <td><strong>${folio}</strong></td>
                <td>
                    <div>${solicitanteEmail}</div>
                </td>
                <td>${solicitanteDept}</td>
                <td>${sol.tipo_pago || 'N/A'}</td>
                <td>
                    <div>${beneficiarioNombre}</div>
                    <small style="color: #64748b;">${bancoDestino}</small>
                </td>
                <td>
                    <strong>${formatearMoneda(monto)}</strong>
                    <br><small style="color: #64748b;">${moneda}</small>
                </td>
                <td>
                    <span class="badge badge-${estadoClass}">${estadoTexto}</span>
                    ${sol.estado === 'pagada' && sol.dias_restantes_comprobante !== null ? 
                        `<br><small style="color: ${sol.dias_restantes_comprobante > 0 ? '#10b981' : '#ef4444'};">
                            ${sol.dias_restantes_comprobante > 0 ? 
                                `${sol.dias_restantes_comprobante} días para comprobante` : 
                                'Plazo vencido'}
                        </small>` : ''
                    }
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-info" onclick="verDetalles('${sol.id}')">
                            <i class="fas fa-eye"></i> Ver
                        </button>
                        ${sol.estado === 'aprobada' ? 
                            `<button class="btn btn-sm btn-success" onclick="abrirModalPagar('${sol.id}')">
                                <i class="fas fa-money-check-alt"></i> Pagar
                            </button>` : ''
                        }
                        ${sol.estado === 'pagada' ? 
                            `<button class="btn btn-sm btn-primary" onclick="abrirModalComprobantes('${sol.id}')">
                                <i class="fas fa-file-upload"></i> Comprobantes (${sol.comprobantes_pago?.length || 0})
                            </button>` : ''
                        }
                    </div>
                </td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
    `;
    
    container.innerHTML = html;
}

function mostrarCargando() {
    const container = document.getElementById('tabla-solicitudes-container');
    container.innerHTML = `
        <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Cargando solicitudes...</p>
        </div>
    `;
}

function mostrarErrorTabla() {
    const container = document.getElementById('tabla-solicitudes-container');
    container.innerHTML = `
        <div class="loading-spinner">
            <i class="fas fa-exclamation-triangle" style="color: var(--danger-color);"></i>
            <p>Error al cargar las solicitudes</p>
            <button class="btn btn-primary" onclick="cargarSolicitudesAprobadas()">
                <i class="fas fa-sync-alt"></i> Reintentar
            </button>
        </div>
    `;
}

// ========================================
// Modales
// ========================================
function abrirModalPagar(solicitudId) {
    const solicitud = solicitudesAprobadas.find(s => s.id === solicitudId);
    if (!solicitud) return;
    
    document.getElementById('pagar-solicitud-id').value = solicitudId;
    document.getElementById('pagar-referencia').value = '';
    document.getElementById('pagar-comentarios').value = '';
    
    document.getElementById('pagar-info-solicitud').innerHTML = `
        <strong>Solicitud:</strong> ${solicitud.folio}<br>
        <strong>Solicitante:</strong> ${solicitud.nombre_solicitante}<br>
        <strong>Monto:</strong> ${formatearMoneda(solicitud.monto_total)} ${solicitud.moneda}<br>
        <strong>Beneficiario:</strong> ${solicitud.beneficiario.nombre}
    `;
    
    abrirModal('modal-pagar');
}

function abrirModalComprobantes(solicitudId) {
    const solicitud = solicitudesAprobadas.find(s => s.id === solicitudId);
    if (!solicitud) return;
    
    document.getElementById('comprobantes-solicitud-id').value = solicitudId;
    archivosSeleccionados = [];
    actualizarListaArchivos();
    
    document.getElementById('comprobantes-info-solicitud').innerHTML = `
        <strong>Solicitud:</strong> ${solicitud.folio}<br>
        <strong>Monto:</strong> ${formatearMoneda(solicitud.monto_total)}<br>
        ${solicitud.dias_restantes_comprobante !== null ? 
            `<strong>Tiempo restante:</strong> ${solicitud.dias_restantes_comprobante} días hábiles` : ''
        }
    `;
    
    // Mostrar comprobantes existentes
    if (solicitud.comprobantes_pago && solicitud.comprobantes_pago.length > 0) {
        const comprobantesGrid = document.getElementById('comprobantes-grid');
        comprobantesGrid.innerHTML = '';
        
        solicitud.comprobantes_pago.forEach(comp => {
            const icon = obtenerIconoArchivo(comp.nombre);
            comprobantesGrid.innerHTML += `
                <div class="comprobante-card">
                    <i class="${icon}"></i>
                    <div class="comprobante-card-nombre" title="${comp.nombre}">${comp.nombre}</div>
                    <div class="comprobante-card-info">${formatearTamaño(comp.tamaño)}</div>
                    <div class="comprobante-card-actions">
                        <button class="btn btn-sm btn-info" onclick="window.open('${comp.ruta}', '_blank')">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-primary" onclick="descargarArchivo('${comp.ruta}', '${comp.nombre}')">
                            <i class="fas fa-download"></i>
                        </button>
                    </div>
                </div>
            `;
        });
        
        document.getElementById('comprobantes-existentes').style.display = 'block';
    } else {
        document.getElementById('comprobantes-existentes').style.display = 'none';
    }
    
    abrirModal('modal-comprobantes');
}

async function verDetalles(solicitudId) {
    abrirModal('modal-detalles');
    
    const detallesContent = document.getElementById('detalles-content');
    detallesContent.innerHTML = `
        <div class="loading-spinner">
            <i class="fas fa-spinner fa-spin"></i>
            <p>Cargando detalles...</p>
        </div>
    `;
    
    try {
        const response = await fetch(`/pagador/api/solicitud/${solicitudId}`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
        });
        
        if (!response.ok) throw new Error('Error al cargar detalles');
        
        const data = await response.json();
        const sol = data.solicitud;
        
        console.log('📋 Datos de solicitud recibidos:', sol);
        
        // Helper function para valores seguros
        const safe = (value, defaultValue = 'N/A') => value || defaultValue;
        
        // Generar folio si no existe
        const folio = sol.folio || `SOL-${sol.id?.substring(0, 8).toUpperCase() || 'XXXXX'}`;
        
        detallesContent.innerHTML = `
            <div class="detalles-grid">
                <div class="detalle-section">
                    <h3><i class="fas fa-info-circle"></i> Información General</h3>
                    <table class="detalles-table">
                        <tr><th>ID:</th><td><strong>${folio}</strong></td></tr>
                        <tr><th>Estado:</th><td><span class="badge badge-${obtenerClaseEstado(sol.estado)}">${safe(sol.estado).toUpperCase()}</span></td></tr>
                        <tr><th>Tipo de Pago:</th><td>${safe(sol.tipo_pago)}</td></tr>
                        <tr><th>Concepto:</th><td>${safe(sol.concepto_pago)}</td></tr>
                        ${sol.concepto_otros ? `<tr><th>Concepto (Otros):</th><td>${sol.concepto_otros}</td></tr>` : ''}
                        <tr><th>Descripción:</th><td>${safe(sol.descripcion_tipo_pago)}</td></tr>
                        ${sol.fecha_limite_pago ? `<tr><th>Fecha Límite Pago:</th><td>${formatearFecha(sol.fecha_limite_pago)}</td></tr>` : ''}
                    </table>
                </div>
                
                <div class="detalle-section">
                    <h3><i class="fas fa-dollar-sign"></i> Información Financiera</h3>
                    <table class="detalles-table">
                        <tr><th>Monto:</th><td><strong>${sol.monto ? formatearMoneda(sol.monto) : 'N/A'}</strong></td></tr>
                        <tr><th>Moneda:</th><td>${safe(sol.tipo_moneda)}</td></tr>
                        <tr><th>Beneficiario:</th><td>${safe(sol.nombre_beneficiario)}</td></tr>
                        ${sol.segundo_beneficiario ? `<tr><th>Segundo Beneficiario:</th><td>${sol.segundo_beneficiario}</td></tr>` : ''}
                        ${sol.nombre_empresa ? `<tr><th>Empresa:</th><td>${sol.nombre_empresa}</td></tr>` : ''}
                        <tr><th>Banco:</th><td>${safe(sol.banco_destino)}</td></tr>
                        <tr><th>${sol.es_clabe ? 'CLABE' : 'Cuenta'}:</th><td>${safe(sol.cuenta_destino)}</td></tr>
                    </table>
                </div>
                
                <div class="detalle-section">
                    <h3><i class="fas fa-user"></i> Información del Solicitante</h3>
                    <table class="detalles-table">
                        <tr><th>Email:</th><td>${safe(sol.solicitante_email)}</td></tr>
                        <tr><th>Departamento:</th><td>${safe(sol.departamento)}</td></tr>
                        <tr><th>Fecha Creación:</th><td>${sol.fecha_creacion ? formatearFecha(sol.fecha_creacion) : 'N/A'}</td></tr>
                        ${sol.comentarios_solicitante ? `<tr><th>Comentarios:</th><td>${sol.comentarios_solicitante}</td></tr>` : ''}
                    </table>
                </div>
                
                ${sol.estado === 'aprobada' || sol.estado === 'pagada' ? `
                    <div class="detalle-section">
                        <h3><i class="fas fa-check-circle"></i> Información de Aprobación</h3>
                        <table class="detalles-table">
                            <tr><th>Aprobado por:</th><td>${safe(sol.aprobador_email)}</td></tr>
                            <tr><th>Fecha Aprobación:</th><td>${sol.fecha_aprobacion ? formatearFecha(sol.fecha_aprobacion) : 'N/A'}</td></tr>
                            <tr><th>Comentarios:</th><td>${safe(sol.comentarios_aprobador)}</td></tr>
                        </table>
                    </div>
                ` : ''}
                
                ${sol.estado === 'pagada' ? `
                    <div class="detalle-section">
                        <h3><i class="fas fa-money-check-alt"></i> Información de Pago</h3>
                        <table class="detalles-table">
                            <tr><th>Fecha de Pago:</th><td>${sol.fecha_pago ? formatearFecha(sol.fecha_pago) : 'N/A'}</td></tr>
                            <tr><th>Referencia:</th><td>${safe(sol.referencia_pago)}</td></tr>
                            <tr><th>Pagado por:</th><td>${safe(sol.pagador_email)}</td></tr>
                            <tr><th>Comprobantes:</th><td>${sol.comprobantes_pago?.length || 0}</td></tr>
                            <tr><th>Comentarios:</th><td>${safe(sol.comentarios_pagador)}</td></tr>
                            ${sol.fecha_limite_comprobante ? 
                                `<tr><th>Fecha Límite Comprobante:</th><td>${formatearFecha(sol.fecha_limite_comprobante)}</td></tr>` : ''
                            }
                        </table>
                    </div>
                ` : ''}
                
                ${sol.archivos_adjuntos && sol.archivos_adjuntos.length > 0 ? `
                    <div class="detalle-section" style="grid-column: 1 / -1;">
                        <h3><i class="fas fa-paperclip"></i> Archivos Adjuntos (${sol.archivos_adjuntos.length})</h3>
                        <div class="archivos-grid">
                            ${sol.archivos_adjuntos.map(archivo => {
                                const extension = archivo.nombre?.split('.').pop()?.toLowerCase() || '';
                                const iconClass = obtenerClaseIconoArchivo(archivo.nombre || '').replace('icon-', '');
                                return `
                                    <div class="archivo-card" onclick="window.open('${archivo.ruta}', '_blank')">
                                        <div class="archivo-preview preview-${iconClass}">
                                            <i class="${obtenerIconoArchivo(archivo.nombre || '')}"></i>
                                        </div>
                                        <div class="archivo-info">
                                            <div class="archivo-nombre" title="${archivo.nombre}">${archivo.nombre}</div>
                                            <div class="archivo-meta">
                                                <span class="archivo-extension">${extension.toUpperCase()}</span>
                                                <span class="archivo-tamaño">${formatearTamaño(archivo.tamaño || archivo.size || 0)}</span>
                                            </div>
                                        </div>
                                        <div class="archivo-acciones">
                                            <button class="btn btn-sm btn-primary" onclick="event.stopPropagation(); descargarArchivo('${archivo.ruta}', '${archivo.nombre}')">
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
        `;
        
    } catch (error) {
        console.error('Error al cargar detalles:', error);
        detallesContent.innerHTML = `
            <div class="loading-spinner">
                <i class="fas fa-exclamation-triangle" style="color: var(--danger-color);"></i>
                <p>Error al cargar los detalles</p>
            </div>
        `;
    }
}

function abrirModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        modal.style.display = 'flex';
    }
}

function cerrarModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        modal.style.display = 'none';
    }
}

// ========================================
// Acciones de Pago
// ========================================
async function confirmarPago() {
    const solicitudId = document.getElementById('pagar-solicitud-id').value;
    const referencia = document.getElementById('pagar-referencia').value.trim();
    const comentarios = document.getElementById('pagar-comentarios').value.trim();
    
    if (!solicitudId) {
        mostrarToast('Error: ID de solicitud no válido', 'error');
        return;
    }
    
    const btnConfirmar = document.getElementById('btn-confirmar-pagar');
    btnConfirmar.disabled = true;
    btnConfirmar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
    
    try {
        const requestData = {
            solicitud_id: solicitudId
        };
        
        if (referencia) {
            requestData.referencia_pago = referencia;
        }
        
        if (comentarios) {
            requestData.comentarios_pagador = comentarios;
        }
        
        console.log('📤 Enviando pago:', requestData);
        
        const response = await fetch('/pagador/api/marcar-pagada', {
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
            throw new Error(data.detail || 'Error al marcar como pagada');
        }
        
        // Éxito
        mostrarToast('✅ Solicitud marcada como pagada exitosamente', 'success');
        cerrarModal('modal-pagar');
        
        // Refrescar datos
        await cargarEstadisticas();
        await cargarSolicitudesAprobadas();
        
    } catch (error) {
        console.error('Error al marcar como pagada:', error);
        mostrarToast(`Error: ${error.message}`, 'error');
    } finally {
        btnConfirmar.disabled = false;
        btnConfirmar.innerHTML = '<i class="fas fa-check"></i> Marcar como Pagada';
    }
}

// ========================================
// Upload de Archivos
// ========================================
function inicializarUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('comprobantes-archivos');
    
    // Click en el área de upload
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // Cambio en el input de archivo
    fileInput.addEventListener('change', (e) => {
        agregarArchivos(Array.from(e.target.files));
    });
    
    // Drag & Drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        agregarArchivos(Array.from(e.dataTransfer.files));
    });
}

function agregarArchivos(nuevosArchivos) {
    archivosSeleccionados.push(...nuevosArchivos);
    actualizarListaArchivos();
}

function actualizarListaArchivos() {
    const archivosLista = document.getElementById('archivos-lista');
    const archivosSection = document.getElementById('archivos-seleccionados');
    const btnSubir = document.getElementById('btn-subir-comprobantes');
    
    if (archivosSeleccionados.length === 0) {
        archivosSection.style.display = 'none';
        btnSubir.disabled = true;
        return;
    }
    
    archivosSection.style.display = 'block';
    btnSubir.disabled = false;
    
    archivosLista.innerHTML = '';
    
    archivosSeleccionados.forEach((archivo, index) => {
        const icon = obtenerIconoArchivo(archivo.name);
        const iconClass = obtenerClaseIconoArchivo(archivo.name);
        
        archivosLista.innerHTML += `
            <div class="archivo-item">
                <div class="archivo-item-info">
                    <div class="archivo-item-icon ${iconClass}">
                        <i class="${icon}"></i>
                    </div>
                    <div class="archivo-item-details">
                        <div class="archivo-item-nombre">${archivo.name}</div>
                        <div class="archivo-item-meta">${formatearTamaño(archivo.size)}</div>
                    </div>
                </div>
                <button class="archivo-item-remove" onclick="eliminarArchivo(${index})">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    });
}

function eliminarArchivo(index) {
    archivosSeleccionados.splice(index, 1);
    actualizarListaArchivos();
}

async function subirComprobantes() {
    const solicitudId = document.getElementById('comprobantes-solicitud-id').value;
    
    if (!solicitudId) {
        mostrarToast('Error: ID de solicitud no válido', 'error');
        return;
    }
    
    if (archivosSeleccionados.length === 0) {
        mostrarToast('Debe seleccionar al menos un archivo', 'warning');
        return;
    }
    
    const btnSubir = document.getElementById('btn-subir-comprobantes');
    btnSubir.disabled = true;
    btnSubir.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Subiendo...';
    
    try {
        const formData = new FormData();
        formData.append('solicitud_id', solicitudId);
        
        archivosSeleccionados.forEach(archivo => {
            formData.append('archivos', archivo);
        });
        
        console.log(`📤 Subiendo ${archivosSeleccionados.length} archivos...`);
        
        const response = await fetch('/pagador/api/subir-comprobantes', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            console.error('❌ Error en respuesta:', data);
            throw new Error(data.detail || 'Error al subir comprobantes');
        }
        
        // Éxito
        mostrarToast(`✅ ${data.archivos_subidos} comprobantes subidos exitosamente`, 'success');
        cerrarModal('modal-comprobantes');
        
        // Refrescar datos
        await cargarEstadisticas();
        await cargarSolicitudesAprobadas();
        
    } catch (error) {
        console.error('Error al subir comprobantes:', error);
        mostrarToast(`Error: ${error.message}`, 'error');
    } finally {
        btnSubir.disabled = false;
        btnSubir.innerHTML = '<i class="fas fa-upload"></i> Subir Comprobantes';
    }
}

// ========================================
// Filtros
// ========================================
function aplicarFiltros() {
    filtrosAplicados.departamento = document.getElementById('filtro-departamento').value;
    filtrosAplicados.tipo_pago = document.getElementById('filtro-tipo-pago').value;
    cargarSolicitudesAprobadas();
}

function limpiarFiltros() {
    document.getElementById('filtro-departamento').value = '';
    document.getElementById('filtro-tipo-pago').value = '';
    filtrosAplicados = { departamento: '', tipo_pago: '' };
    cargarSolicitudesAprobadas();
}

function refrescar() {
    cargarEstadisticas();
    cargarSolicitudesAprobadas();
    mostrarToast('Datos actualizados', 'success');
}

// ========================================
// Funciones Auxiliares
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
        'aprobada': 'aprobada',
        'pagada': 'pagada',
        'enviada': 'enviada'
    };
    return clases[estado] || 'default';
}

function obtenerIconoArchivo(nombreArchivo) {
    const extension = nombreArchivo.split('.').pop().toLowerCase();
    
    const iconos = {
        'pdf': 'fas fa-file-pdf',
        'doc': 'fas fa-file-word',
        'docx': 'fas fa-file-word',
        'xls': 'fas fa-file-excel',
        'xlsx': 'fas fa-file-excel',
        'csv': 'fas fa-file-excel',
        'jpg': 'fas fa-file-image',
        'jpeg': 'fas fa-file-image',
        'png': 'fas fa-file-image',
        'gif': 'fas fa-file-image',
        'webp': 'fas fa-file-image',
        'svg': 'fas fa-file-image'
    };
    
    return iconos[extension] || 'fas fa-file';
}

function obtenerClaseIconoArchivo(nombreArchivo) {
    const extension = nombreArchivo.split('.').pop().toLowerCase();
    
    if (['pdf'].includes(extension)) return 'icon-pdf';
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'].includes(extension)) return 'icon-image';
    if (['xls', 'xlsx', 'csv'].includes(extension)) return 'icon-excel';
    if (['doc', 'docx'].includes(extension)) return 'icon-word';
    
    return 'icon-default';
}

function descargarArchivo(ruta, nombre) {
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

console.log('✅ Dashboard de Pagador cargado correctamente');
