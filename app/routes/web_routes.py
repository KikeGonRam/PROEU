from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app.routes.user_routes import get_current_admin_user
from app.middleware.auth_middleware import get_current_user, get_optional_current_user
from app.models.user import UserResponse, UserRole
from app.controllers.user_controller import user_controller

# Configurar router y templates
router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse, summary="Página principal")
async def root(request: Request):
    """
    Redirige a la página de login o home según autenticación.
    """
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "title": "Iniciar Sesión"
    })

@router.get("/home", response_class=HTMLResponse, summary="Dashboard principal")
async def home(request: Request):
    """
    Dashboard principal del sistema.
    """
    return templates.TemplateResponse("home.html", {
        "request": request,
        "title": "Dashboard - Sistema de Solicitudes de Pagos"
    })

@router.get("/users", response_class=HTMLResponse, summary="Página de gestión de usuarios")
async def users_page(request: Request):
    """
    Página para gestión de usuarios.
    Solo accesible por administradores.
    """
    return templates.TemplateResponse("users.html", {
        "request": request,
        "title": "Gestión de Usuarios"
    })


@router.get("/users/charts", response_class=HTMLResponse, summary="Estadísticas de usuarios")
async def users_charts_page(request: Request):
    """
    Página con gráficas y estadísticas de usuarios (solo admin).
    Intentamos obtener el token desde el Authorization header o desde la
    cookie "access_token" (esta cookie se define al iniciar sesión).

    Devuelve 403 si no hay token válido o si el usuario no es administrador.
    """
    # 1) Intentar leer Authorization header
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    # Debug log: print incoming headers and cookies to server stdout to help diagnose missing cookie
    try:
        print(f"[DEBUG] /users/charts request Authorization header: {auth_header}")
        print(f"[DEBUG] /users/charts request.cookies: {request.cookies}")
    except Exception:
        pass
    token = None
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split()[1]
    else:
        # 2) Intentar leer cookie (set by login route)
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=403, detail="Acceso denegado. Solo administradores.")

    # Verificar token y obtener email
    email = user_controller.verify_token(token)
    if email is None:
        raise HTTPException(status_code=403, detail="Token inválido o expirado")

    # Obtener usuario y verificar rol
    user = await user_controller.get_user_by_email(email)
    if user is None or (user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Acceso denegado. Se requiere rol de administrador.")

    return templates.TemplateResponse("users/charts.html", {
        "request": request,
        "title": "Estadísticas de Usuarios",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }
    })


@router.get("/requests/charts", response_class=HTMLResponse, summary="Estadísticas de solicitudes")
async def requests_charts_page(request: Request):
    """
    Página con gráficas y estadísticas de solicitudes (solo admin).
    """
    # Intentar leer Authorization header o cookie
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    try:
        print(f"[DEBUG] /requests/charts request Authorization header: {auth_header}")
        print(f"[DEBUG] /requests/charts request.cookies: {request.cookies}")
    except Exception:
        pass

    token = None
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split()[1]
    else:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=403, detail="Acceso denegado. Solo administradores.")

    email = user_controller.verify_token(token)
    if email is None:
        raise HTTPException(status_code=403, detail="Token inválido o expirado")

    user = await user_controller.get_user_by_email(email)
    if user is None or (user.role != UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Acceso denegado. Se requiere rol de administrador.")

    return templates.TemplateResponse("requests/charts.html", {
        "request": request,
        "title": "Estadísticas de Solicitudes",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }
    })


@router.get("/aprobador/charts", response_class=HTMLResponse, summary="Estadísticas del Aprobador")
async def aprobador_charts_page(request: Request):
    """
    Página con gráficas y estadísticas específicas para el aprobador.
    Accesible por usuarios con rol 'aprobador' o 'admin'.
    """
    # Intentar leer Authorization header o cookie
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    try:
        print(f"[DEBUG] /aprobador/charts request Authorization header: {auth_header}")
        print(f"[DEBUG] /aprobador/charts request.cookies: {request.cookies}")
    except Exception:
        pass

    token = None
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split()[1]
    else:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=403, detail="Acceso denegado. Se requiere rol de aprobador.")

    email = user_controller.verify_token(token)
    if email is None:
        raise HTTPException(status_code=403, detail="Token inválido o expirado")

    user = await user_controller.get_user_by_email(email)
    # Allow either aprobador or admin
    if user is None or (user.role not in (UserRole.APROBADOR, UserRole.ADMIN)):
        raise HTTPException(status_code=403, detail="Acceso denegado. Se requiere rol de aprobador.")

    return templates.TemplateResponse("aprobador/charts.html", {
        "request": request,
        "title": "Estadísticas Aprobador",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
        }
    })

@router.get("/login", response_class=HTMLResponse, summary="Página de login")
async def login_page(request: Request):
    """
    Página de inicio de sesión.
    """
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "title": "Iniciar Sesión"
    })


@router.get('/debug/headers')
async def debug_headers(request: Request):
    """Debug endpoint that returns incoming request headers and cookies as JSON.
    Use this to verify whether the browser is sending the access_token cookie.
    """
    # Convert headers to a normal dict (may contain bytes) and cookies
    headers = dict(request.headers)
    cookies = dict(request.cookies)
    return {"headers": headers, "cookies": cookies}

@router.get("/register", response_class=HTMLResponse, summary="Página de registro")
async def register_page(request: Request):
    """
    Página de registro de nuevos usuarios.
    """
    return templates.TemplateResponse("auth/register.html", {
        "request": request,
        "title": "Registro"
    })

@router.get("/dashboard-solicitante", response_class=HTMLResponse, summary="Dashboard del solicitante")
async def dashboard_solicitante(request: Request):
    """
    Dashboard específico para usuarios con rol de solicitante.
    """
    return templates.TemplateResponse("dashboards/solicitante.html", {
        "request": request,
        "title": "Dashboard Solicitante - Sistema de Solicitudes de Pagos"
    })

@router.get("/dashboard-aprobador", response_class=HTMLResponse, summary="Dashboard del aprobador")
async def dashboard_aprobador(request: Request):
    """
    Dashboard específico para usuarios con rol de aprobador.
    """
    return templates.TemplateResponse("dashboards/aprobador.html", {
        "request": request,
        "title": "Dashboard Aprobador - Sistema de Solicitudes de Pagos"
    })

@router.get("/dashboard-pagador", response_class=HTMLResponse, summary="Dashboard del pagador")
async def dashboard_pagador(request: Request):
    """
    Dashboard específico para usuarios con rol de pagador.
    """
    return templates.TemplateResponse("dashboards/pagador.html", {
        "request": request,
        "title": "Dashboard Pagador - Sistema de Solicitudes de Pagos"
    })

@router.get("/solicitud-estandar/nueva", response_class=HTMLResponse, summary="Nueva solicitud estándar")
async def nueva_solicitud_estandar(request: Request):
    """
    Formulario para crear una nueva solicitud estándar.
    """
    return templates.TemplateResponse("solicitudes/estandar.html", {
        "request": request,
        "title": "Nueva Solicitud Estándar - Sistema de Solicitudes de Pagos"
    })

@router.get("/solicitud-estandar/editar", response_class=HTMLResponse, summary="Editar solicitud estándar")
async def editar_solicitud_estandar(request: Request):
    """
    Formulario para editar una solicitud estándar existente.
    """
    return templates.TemplateResponse("solicitudes/editar.html", {
        "request": request,
        "title": "Editar Solicitud Estándar - Sistema de Solicitudes de Pagos"
    })

@router.get("/dashboard", response_class=HTMLResponse, summary="Dashboard principal")
async def dashboard(request: Request):
    """
    Dashboard principal del sistema.
    """
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Dashboard"
    })

@router.get("/requests", response_class=HTMLResponse, summary="Página de solicitudes")
async def requests_page(request: Request):
    """
    Página para gestión de solicitudes de pagos.
    """
    return templates.TemplateResponse("requests/list.html", {
        "request": request,
        "title": "Solicitudes de Pagos"
    })

@router.get("/requests-list", response_class=HTMLResponse, summary="Lista de solicitudes")
async def requests_list_page(request: Request):
    """
    Alias para la página de lista de solicitudes.
    """
    return templates.TemplateResponse("requests/list.html", {
        "request": request,
        "title": "Solicitudes de Pagos"
    })


@router.get("/profile", response_class=HTMLResponse, summary="Perfil de usuario")
async def profile_page(request: Request, current_user: dict | None = Depends(get_optional_current_user)):
    """
    Página de perfil del usuario. Si el visitante está autenticado, se inyecta
    `user` con la información; si no, `user` será None y la plantilla mostrará
    el contenido público / mensaje de inicio de sesión.
    """
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "title": "Mi Perfil",
        "user": current_user
    })


@router.get("/settings", response_class=HTMLResponse, summary="Configuración del usuario")
async def settings_page(request: Request, current_user: dict | None = Depends(get_optional_current_user)):
    """
    Página de configuración del usuario. Si el visitante está autenticado, se
    inyecta `user` para que el cliente muestre las opciones por rol; si no,
    la página sigue siendo accesible y mostrará un mensaje o invitación a iniciar
    sesión en el cliente.
    """
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "title": "Configuración",
        "user": current_user
    })