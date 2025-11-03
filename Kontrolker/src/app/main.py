# src/app/main.py
from pathlib import Path

from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

from app.routers import projects_router, services_router
from app.db.session import engine
from app.models import Base

app = FastAPI(title="Kontrolker API")

# crea tablas
Base.metadata.create_all(bind=engine)

# ruta absoluta al directorio static
BASE_DIR = Path(__file__).resolve().parent  # = src/app
STATIC_DIR = BASE_DIR / "static"

# solo la montamos si existe, para que no truene
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/favicon.ico")
    async def favicon():
        return FileResponse(str(STATIC_DIR / "favicon.ico"))

# router padre con versión
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(projects_router)
api_router.include_router(services_router)

app.include_router(api_router)
