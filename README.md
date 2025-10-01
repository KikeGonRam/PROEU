# Sistema de Solicitudes de Pagos

Un sistema web moderno para optimizar las solicitudes de pagos departamentales de una empresa, desarrollado con FastAPI y MongoDB.

## 🚀 Características

- **Gestión de Usuarios**: CRUD completo con roles (Administrador, Solicitante)
- **Autenticación JWT**: Sistema seguro de autenticación y autorización
- **Interfaz Moderna**: UI responsiva con Tailwind CSS
- **API REST**: Documentación automática con Swagger/OpenAPI
- **Base de Datos NoSQL**: MongoDB para flexibilidad y escalabilidad
- **Validaciones**: Validaciones robustas con Pydantic
- **Paginación y Filtros**: Búsqueda y filtrado avanzado

## 🛠️ Tecnologías

- **Backend**: FastAPI (Python)
- **Base de Datos**: MongoDB
- **Frontend**: HTML5, CSS3 (Tailwind), JavaScript
- **Autenticación**: JWT (JSON Web Tokens)
- **Validaciones**: Pydantic
- **Documentación**: Swagger UI automática

## 📋 Prerrequisitos

- Python 3.8+
- MongoDB 4.4+
- Git

## 🔧 Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <tu-repositorio>
   cd PROYECTO
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   # Copiar archivo de ejemplo
   copy .env.example .env
   
   # Editar .env con tus configuraciones
   ```

5. **Iniciar MongoDB**
   ```bash
   # Asegúrate de que MongoDB esté ejecutándose
   mongod
   ```

6. **Ejecutar la aplicación**
   ```bash
   python main.py
   ```

7. **Acceder a la aplicación**
   - Aplicación Web: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 📁 Estructura del Proyecto

```
PROYECTO/
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── database.py      # Configuración de MongoDB
│   │   └── settings.py      # Variables de entorno
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── user_controller.py  # Lógica de negocio de usuarios
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # Modelos de datos con Pydantic
│   └── routes/
│       ├── __init__.py
│       ├── user_routes.py   # Rutas API de usuarios
│       └── web_routes.py    # Rutas web (HTML)
├── static/
│   ├── css/
│   │   └── custom.css       # Estilos personalizados
│   └── js/
│       ├── main.js          # JavaScript principal
│       └── users.js         # JavaScript específico de usuarios
├── templates/
│   ├── base.html            # Plantilla base
│   └── users/
│       └── list.html        # Lista de usuarios
├── main.py                  # Punto de entrada de la aplicación
├── requirements.txt         # Dependencias de Python
├── .env.example            # Variables de entorno ejemplo
└── README.md               # Este archivo
```

## 🔐 Configuración de Seguridad

### Variables de Entorno Importantes

```env
# Cambiar en producción
SECRET_KEY=tu-clave-secreta-muy-segura
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=sistema_solicitudes_pagos
```

### Crear Usuario Administrador

Para crear el primer usuario administrador, puedes usar la API:

```bash
curl -X POST "http://localhost:8000/api/users" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@empresa.com",
       "password": "admin123456",
       "first_name": "Administrador",
       "last_name": "Sistema",
       "department": "TI",
       "role": "admin"
     }'
```

## 📚 API Endpoints

### Autenticación
- `POST /api/users/login` - Iniciar sesión
- `GET /api/users/me` - Perfil del usuario actual

### Gestión de Usuarios (Solo Administradores)
- `GET /api/users` - Listar usuarios con filtros y paginación
- `POST /api/users` - Crear nuevo usuario
- `GET /api/users/{id}` - Obtener usuario específico
- `PUT /api/users/{id}` - Actualizar usuario
- `DELETE /api/users/{id}` - Eliminar usuario
- `PATCH /api/users/{id}/status` - Cambiar estado de usuario
- `PATCH /api/users/{id}/role` - Cambiar rol de usuario

### Rutas Web
- `GET /` - Página principal
- `GET /users` - Gestión de usuarios (interfaz web)
- `GET /login` - Página de login
- `GET /dashboard` - Dashboard principal

## 🎨 Interfaz de Usuario

### Características de la UI
- **Responsive**: Adaptable a móviles y tablets
- **Tailwind CSS**: Framework CSS utilitario moderno
- **Iconos**: Font Awesome para iconografía
- **Componentes**: Modales, tablas, formularios, paginación
- **Notificaciones**: Sistema de alertas dinámicas

### Roles y Permisos
- **Administrador**: Acceso completo al sistema
- **Solicitante**: Acceso limitado (para futuras funcionalidades)

## 🚧 Próximas Funcionalidades

1. **Módulo de Solicitudes de Pagos**
   - Crear, editar, eliminar solicitudes
   - Workflow de aprobación
   - Estados de solicitud
   - Adjuntar documentos

2. **Sistema de Notificaciones**
   - Notificaciones por email
   - Notificaciones en tiempo real
   - Panel de notificaciones

3. **Reportes y Dashboards**
   - Estadísticas de solicitudes
   - Gráficos interactivos
   - Exportación de reportes

4. **Configuración de Empresa**
   - Configuración de departamentos
   - Configuración de tipos de pago
   - Configuración de flujos de aprobación

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es parte de un proyecto educativo para la materia de Experiencia de Usuario en UTVT.

## 👥 Equipo de Desarrollo

- **Proyecto Educativo**: UTVT - Experiencia de Usuario
- **Año**: 2025

## 📞 Soporte

Para soporte técnico o preguntas sobre el proyecto, contacta a tu instructor de la materia.

---

**Nota**: Este es un proyecto educativo desarrollado para fines académicos en la Universidad Tecnológica del Valle de Toluca (UTVT).