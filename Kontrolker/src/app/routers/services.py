# src.app/routers/services.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session

from ..schemas import ServiceCreate, ServiceRead, ServiceUpdate
from ..db.deps import get_db
from ..models.service import Service
from ..models.project import Project
# app/routers/services.py


router = APIRouter(
    prefix="/services",
    tags=["Services"],
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


def _ensure_service_exists(db: Session, service_id: int) -> Service:
    svc = (
        db.query(Service)
        .filter(Service.id == service_id, Service.deleted_at.is_(None))
        .first()
    )
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    return svc


@router.post(
    "",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un Service",
    description="Crea una definición lógica de servicio que podrá usarse para levantar contenedores.",
    responses={
        201: {
            "description": "Service creado correctamente",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "project_id": 1,
                        "name": "postgres-db",
                        "image": "postgres:16",
                        "ports": [
                            {"host": 5432, "container": 5432}
                        ],
                        "env": {
                            "POSTGRES_USER": "admin",
                            "POSTGRES_PASSWORD": "secret",
                            "POSTGRES_DB": "kontrolker"
                        },
                        "resources": {
                            "cpu": 1.0,
                            "memory_mb": 512
                        },
                        "created_at": "2025-11-10T12:10:00Z",
                        "updated_at": "2025-11-10T12:10:00Z"
                    }
                }
            },
        },
        404: {"description": "Project not found"},
        409: {"description": "Service name must be unique within project"},
        422: {"description": "Error de validación (puertos, imagen, recursos, env...)"},
    },
)
def create_service(
    payload: ServiceCreate = Body(
        ...,
        examples={
            "postgresService": {
                "summary": "Service para Postgres",
                "value": {
                    "project_id": 1,
                    "name": "postgres-db",
                    "image": "postgres:16",
                    "ports": [
                        {"host": 5432, "container": 5432}
                    ],
                    "env": {
                        "POSTGRES_USER": "admin",
                        "POSTGRES_PASSWORD": "secret",
                        "POSTGRES_DB": "kontrolker"
                    },
                    "resources": {
                        "cpu": 1.0,
                        "memory_mb": 512
                    }
                },
            },
            "nginxService": {
                "summary": "Service para Nginx",
                "value": {
                    "project_id": 1,
                    "name": "nginx-front",
                    "image": "nginx:latest",
                    "ports": [
                        {"host": 8080, "container": 80}
                    ],
                    "env": {},
                    "resources": {
                        "cpu": 0.5,
                        "memory_mb": 256
                    }
                },
            },
        },
    ),
    db: Session = Depends(get_db),
):
    _ensure_project_exists(db, payload.project_id)

    existing = (
        db.query(Service)
        .filter(
            Service.project_id == payload.project_id,
            Service.name == payload.name,
            Service.deleted_at.is_(None),
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service name must be unique within project",
        )

    now = datetime.utcnow()
    svc = Service(
        project_id=payload.project_id,
        name=payload.name,
        image=payload.image,
        ports=[p.model_dump() for p in payload.ports],
        env=payload.env,
        resources=payload.resources.model_dump() if payload.resources else None,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )
    db.add(svc)
    db.commit()
    db.refresh(svc)
    return svc


@router.get(
    "",
    response_model=List[ServiceRead],
    summary="Listar Services",
    description="Lista services, opcionalmente filtrando por project_id.",
    responses={
        200: {
            "description": "Listado de services",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "project_id": 1,
                            "name": "postgres-db",
                            "image": "postgres:16",
                            "ports": [
                                {"host": 5432, "container": 5432}
                            ],
                            "env": {
                                "POSTGRES_USER": "admin",
                                "POSTGRES_PASSWORD": "secret"
                            },
                            "resources": {
                                "cpu": 1.0,
                                "memory_mb": 512
                            },
                            "created_at": "2025-11-10T12:10:00Z",
                            "updated_at": "2025-11-10T12:10:00Z"
                        }
                    ]
                }
            },
        }
    },
)
def list_services(
    project_id: Optional[int] = Query(
        default=None,
        description="Filtrar por project_id",
        examples=[1],
    ),
    db: Session = Depends(get_db),
):
    q = db.query(Service).filter(Service.deleted_at.is_(None))
    if project_id is not None:
        q = q.filter(Service.project_id == project_id)
    return q.all()


@router.get(
    "/{service_id}",
    response_model=ServiceRead,
    summary="Obtener Service por ID",
    responses={
        200: {"description": "Service encontrado"},
        404: {"description": "Service not found"},
    },
)
def get_service(service_id: int, db: Session = Depends(get_db)):
    svc = _ensure_service_exists(db, service_id)
    return svc


@router.patch(
    "/{service_id}",
    response_model=ServiceRead,
    summary="Actualizar parcialmente un Service",
    responses={
        200: {"description": "Service actualizado"},
        404: {"description": "Service not found"},
        409: {"description": "Service name must be unique within project"},
        422: {"description": "Error de validación"},
    },
)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    db: Session = Depends(get_db),
):
    svc = _ensure_service_exists(db, service_id)

    if payload.name is not None:
        conflict = (
            db.query(Service)
            .filter(
                Service.project_id == svc.project_id,
                Service.name == payload.name,
                Service.id != svc.id,
                Service.deleted_at.is_(None),
            )
            .first()
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Service name must be unique within project",
            )
        svc.name = payload.name

    if payload.image is not None:
        svc.image = payload.image

    if payload.ports is not None:
        svc.ports = [p.model_dump() for p in payload.ports]

    if payload.env is not None:
        svc.env = payload.env

    if payload.resources is not None:
        svc.resources = payload.resources.model_dump()

    svc.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(svc)
    return svc


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar Service (soft-delete)",
    responses={
        204: {"description": "Service eliminado (soft-delete)"},
        404: {"description": "Service not found"},
    },
)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    svc = _ensure_service_exists(db, service_id)
    svc.deleted_at = datetime.utcnow()
    db.commit()
    return None
