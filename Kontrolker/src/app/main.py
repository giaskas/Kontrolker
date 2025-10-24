from fastapi import FastAPI, APIRouter
from app.routers import projects, services  # módulos
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse


app = FastAPI(title="Kontrolker API")
app.mount("/static", StaticFiles(directory="src/app/static"), name="static")

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("src/app/static/favicon.ico")

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(projects.router, tags=["Projects"])   
api_router.include_router(services.router, tags=["Services"])   

app.include_router(api_router)
