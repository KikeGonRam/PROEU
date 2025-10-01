from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.routes.user_routes import get_current_admin_user
from app.models.user import UserResponse

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

@router.get("/login", response_class=HTMLResponse, summary="Página de login")
async def login_page(request: Request):
    """
    Página de inicio de sesión.
    """
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "title": "Iniciar Sesión"
    })

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