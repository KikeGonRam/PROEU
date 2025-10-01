from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user_routes, web_routes, solicitud_routes
from app.config.database import connect_to_mongo, close_mongo_connection

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

# Incluir rutas web
app.include_router(web_routes.router, tags=["Web"])

# Ruta principal
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request, "title": "Sistema de Solicitudes de Pagos"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)