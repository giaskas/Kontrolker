from pathlib import Path
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse, JSONResponse
from sqlalchemy import text
from .core.logging import setup_logging
from .core.request_id import RequestIDMiddleware
from .db.session import engine, SessionLocal
from .models import Base
from .routers import projects_router, services_router, containers_router
from .routers.containers import router as containers_router
import docker

setup_logging()
app = FastAPI(title="Kontrolker API")
app.add_middleware(RequestIDMiddleware)

# crea tablas
Base.metadata.create_all(bind=engine)

# static opcional...
# (lo que ya tenías)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(projects_router, tags=["Projects"])
api_router.include_router(services_router, tags=["Services"])
api_router.include_router(containers_router, tags=["Containers"])
app.include_router(api_router)

@app.get("/health", summary="DB + Docker health")
def health():
    ok_db = False
    ok_docker = False
    try:
        with SessionLocal() as s:
            s.execute(text("SELECT 1"))
            ok_db = True
    except Exception:
        ok_db = False

    try:
        docker.from_env().ping()
        ok_docker = True
    except Exception:
        ok_docker = False

    status_code = 200 if (ok_db and ok_docker) else 503
    return JSONResponse(
        status_code=status_code,
        content={"db": ok_db, "docker": ok_docker}
    )
