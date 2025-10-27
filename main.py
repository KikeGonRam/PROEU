from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks, Form, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user_routes, web_routes, solicitud_routes
from app.routes import aprobador, pagador
from app.routes import chat_routes
from app.config.database import connect_to_mongo, close_mongo_connection
import smtplib
from fastapi.responses import HTMLResponse
from app.utils.auth import get_current_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

# Crear instancia de FastAPI
app = FastAPI(
    title="Sistema de Solicitudes de Pagos",
    description="Sistema para optimizar las solicitudes de pagos departamentales",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Incluir rutas de API
app.include_router(user_routes.router, prefix="/api/users", tags=["Usuarios"])
app.include_router(solicitud_routes.router, prefix="/api/solicitudes", tags=["Solicitudes"])

# Incluir rutas del aprobador y pagador
app.include_router(aprobador.router, tags=["Aprobador"])
app.include_router(pagador.router, tags=["Pagador"])

# Incluir rutas web
app.include_router(web_routes.router, tags=["Web"])
app.include_router(chat_routes.router, tags=["Chat"])

# Ruta principal
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request, "title": "Sistema de Solicitudes de Pagos"})

# Ruta para la página de recuperación de contraseña
@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("auth/forgot_password.html", {"request": request, "title": "Recuperar Contraseña"})

# Ruta para manejar la recuperación de contraseña
@app.post("/forgot-password")
async def handle_forgot_password(background_tasks: BackgroundTasks, email: str = Form(...)):
    # Simular envío de correo
    def send_email(to_email):
        try:
            # Configuración del servidor SMTP
            server = smtplib.SMTP("smtp.example.com", 587)
            server.starttls()
            server.login("your_email@example.com", "your_password")

            # Mensaje de correo
            message = f"Subject: Recuperación de Contraseña\n\nHaz clic en el siguiente enlace para restablecer tu contraseña: http://127.0.0.1:8000/reset-password?email={to_email}"
            server.sendmail("your_email@example.com", to_email, message)
            server.quit()
        except Exception as e:
            print(f"Error al enviar correo: {e}")

    # Agregar tarea en segundo plano para enviar el correo
    background_tasks.add_task(send_email, email)
    return {"message": "Si el correo está registrado, recibirás un enlace para restablecer tu contraseña."}

# Ruta para la política de privacidad
@app.get("/privacy", response_class=HTMLResponse)
async def privacy_page(request: Request):
    return templates.TemplateResponse("privacy.html", {"request": request, "title": "Política de Privacidad"})

# Ruta para los términos y condiciones
@app.get("/terms", response_class=HTMLResponse)
async def terms_page(request: Request):
    return templates.TemplateResponse("terms.html", {"request": request, "title": "Términos y Condiciones"})

# Ruta para la página de inicio
@app.get("/home", response_class=HTMLResponse)
async def home(request: Request, user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only")
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)