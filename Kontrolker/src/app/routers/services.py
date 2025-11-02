# routers/services.py
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/services",          # 👈 prefijo propio del recurso
    tags=["Services"],           # 👈 se agrupa en /docs
)

# ====== Schemas (MVP) ======
class Port(BaseModel):
    host: int = Field(ge=1, le=65535)
    container: int = Field(ge=1, le=65535)

class ServiceCreate(BaseModel):
    project_id: int
    name: str
    image: str | None = None
    ports: list[Port] = []

class ServiceRead(BaseModel):
    id: int
    project_id: int
    name: str
    image: str | None = None
    ports: list[Port] = []

# ====== Endpoints ======

@router.post(
    "",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un servicio",
    description="Crea un servicio ligado a un proyecto. `image` es obligatoria en el negocio real."
)
def create_service(payload: ServiceCreate):
    # validación de negocio del paso 8
    if not payload.image:
        raise HTTPException(status_code=422, detail="image is required")

    # ejemplo de duplicado de host port dentro del mismo service
    host_ports = [p.host for p in payload.ports]
    if len(host_ports) != len(set(host_ports)):
        raise HTTPException(status_code=422, detail="Host port duplicated")

    return ServiceRead(
        id=1,
        project_id=payload.project_id,
        name=payload.name,
        image=payload.image,
        ports=payload.ports,
    )


@router.get(
    "",
    response_model=list[ServiceRead],
    summary="Listar servicios (con filtro por proyecto)"
)
def list_services(project_id: int | None = Query(default=None)):
    """
    Si mandas ?project_id=1 te regreso solo los de ese proyecto.
    Si no mandas nada, te regreso todos.
    """
    dummy = [
        ServiceRead(id=1, project_id=1, name="db", image="postgres:16", ports=[]),
        ServiceRead(id=2, project_id=2, name="api", image="myapp:latest", ports=[]),
    ]
    if project_id is not None:
        return [s for s in dummy if s.project_id == project_id]
    return dummy


@router.get(
    "/{service_id}",
    response_model=ServiceRead,
    summary="Obtener servicio por id"
)
def get_service(service_id: int):
    if service_id == 999:
        raise HTTPException(status_code=404, detail="Not found")
    return ServiceRead(
        id=service_id,
        project_id=1,
        name="db",
        image="postgres:16",
        ports=[],
    )
