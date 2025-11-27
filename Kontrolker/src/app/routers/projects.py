# app/routers/projects.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.project import Project
from app.schemas import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


def _ensure_project_exists(db: Session, project_id: int) -> Project:
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.deleted_at.is_(None))
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un Project",
    description="Crea un proyecto lógico que agrupa Services relacionados.",
    responses={
        201: {
            "description": "Project creado correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "mi-backend",
                        "description": "Proyecto principal del backend",
                        "labels": {
                            "env": "dev",
                            "owner": "alberto"
                        },
                        "created_at": "2025-11-10T12:00:00Z",
                        "updated_at": "2025-11-10T12:00:00Z"
                    }
                }
            },
        },
        409: {"description": "Project name must be unique"},
        422: {"description": "Error de validación en el cuerpo de la petición"},
    },
)
def create_project(
    payload: ProjectCreate = Body(
        ...,
        examples={
            "simple": {
                "summary": "Proyecto mínimo",
                "description": "Solo nombre, sin descripción ni labels.",
                "value": {
                    "name": "mi-backend",
                    "description": None,
                    "labels": {}
                },
            },
            "withLabels": {
                "summary": "Proyecto etiquetado",
                "description": "Incluye etiquetas para ambiente y owner.",
                "value": {
                    "name": "kontrolker-platform",
                    "description": "Proyecto raíz de despliegues",
                    "labels": {
                        "env": "prod",
                        "owner": "plat-devops"
                    }
                },
            },
        },
    ),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(Project)
        .filter(
            Project.name == payload.name,
            Project.deleted_at.is_(None),
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project name must be unique",
        )

    now = datetime.utcnow()
    proj = Project(
        name=payload.name,
        description=payload.description,
        labels=payload.labels,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj


@router.get(
    "",
    response_model=List[ProjectRead],
    summary="Listar Projects",
    description="Lista todos los proyectos activos (no eliminados).",
    responses={
        200: {
            "description": "Listado de proyectos",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "name": "mi-backend",
                            "description": "Backend principal",
                            "labels": {"env": "dev"},
                            "created_at": "2025-11-10T12:00:00Z",
                            "updated_at": "2025-11-10T12:00:00Z",
                        }
                    ]
                }
            },
        }
    },
)
def list_projects(
    name: Optional[str] = Query(
        default=None,
        description="Filtro opcional por nombre exacto",
        examples=["mi-backend"],
    ),
    db: Session = Depends(get_db),
):
    q = db.query(Project).filter(Project.deleted_at.is_(None))
    if name is not None:
        q = q.filter(Project.name == name)
    return q.all()


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Obtener Project por ID",
    responses={
        200: {"description": "Project encontrado"},
        404: {"description": "Project not found"},
    },
)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = _ensure_project_exists(db, project_id)
    return project


@router.patch(
    "/{project_id}",
    response_model=ProjectRead,
    summary="Actualizar parcialmente un Project",
    responses={
        200: {"description": "Project actualizado"},
        404: {"description": "Project not found"},
        409: {"description": "Project name must be unique"},
        422: {"description": "Error de validación"},
    },
)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = _ensure_project_exists(db, project_id)

    if payload.name is not None:
        conflict = (
            db.query(Project)
            .filter(
                Project.name == payload.name,
                Project.id != project.id,
                Project.deleted_at.is_(None),
            )
            .first()
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project name must be unique",
            )
        project.name = payload.name

    if payload.description is not None:
        project.description = payload.description

    if payload.labels is not None:
        project.labels = payload.labels

    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    return project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar Project (soft-delete)",
    description="Marca el proyecto como eliminado mediante deleted_at.",
    responses={
        204: {"description": "Project eliminado (soft-delete)"},
        404: {"description": "Project not found"},
    },
)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = _ensure_project_exists(db, project_id)
    project.deleted_at = datetime.utcnow()
    db.commit()
    return None
