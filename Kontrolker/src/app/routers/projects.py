# routers/projects.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(
    prefix="/projects",          # 👈 prefijo propio del recurso
    tags=["Projects"],           # 👈 así se agrupa en /docs
)

# ====== Schemas (MVP) ======
class ProjectCreate(BaseModel):
    name: str

class ProjectRead(BaseModel):
    id: int
    name: str

# ====== Endpoints ======

@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un proyecto",
    description="Crea un proyecto nuevo. El nombre debe ser único."
)
def create_project(payload: ProjectCreate):
    # aquí iría la lógica real de DB
    if payload.name == "repetido":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project name must be unique"
        )
    return ProjectRead(id=1, name=payload.name)


@router.get(
    "",
    response_model=list[ProjectRead],
    summary="Listar proyectos"
)
def list_projects():
    return [
        ProjectRead(id=1, name="Proyecto A"),
        ProjectRead(id=2, name="Proyecto B"),
    ]


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Obtener proyecto por id"
)
def get_project(project_id: int):
    if project_id == 999:
        raise HTTPException(status_code=404, detail="Not found")
    return ProjectRead(id=project_id, name="Proyecto X")
