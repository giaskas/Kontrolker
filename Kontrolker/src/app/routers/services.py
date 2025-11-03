# src.app/routers/services.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlalchemy.orm import Session

from ..schemas import ServiceCreate, ServiceRead, ServiceUpdate
from ..db.deps import get_db
from ..models.service import Service
from ..models.project import Project

router = APIRouter(
    prefix="/services",
    tags=["Services"],
)


@router.post(
    "",
    response_model=ServiceRead,
    status_code=status.HTTP_201_CREATED,
)
def create_service(payload: ServiceCreate, db: Session = Depends(get_db)):
    # 1) validar que exista el project
    project = db.query(Project).filter(
        Project.id == payload.project_id,
        Project.deleted_at.is_(None)
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2) validación de negocio que ya traía tu MVP
    if not payload.image:
        raise HTTPException(status_code=422, detail="image is required")

    now = datetime.utcnow()
    service = Service(
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
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.get(
    "",
    response_model=List[ServiceRead],
    summary="Listar services (con filtro por project_id)"
)
def list_services(
    project_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Service).filter(Service.deleted_at.is_(None))
    if project_id is not None:
        query = query.filter(Service.project_id == project_id)
    return query.all()


@router.get(
    "/{service_id}",
    response_model=ServiceRead,
)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.deleted_at.is_(None)
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Not found")
    return service


@router.patch(
    "/{service_id}",
    response_model=ServiceRead,
)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    db: Session = Depends(get_db),
):
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.deleted_at.is_(None)
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Not found")

    if payload.project_id is not None:
        # validar que exista el nuevo project
        project = db.query(Project).filter(
            Project.id == payload.project_id,
            Project.deleted_at.is_(None)
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        service.project_id = payload.project_id

    if payload.name is not None:
        service.name = payload.name

    if payload.image is not None:
        service.image = payload.image

    if payload.ports is not None:
        service.ports = [p.model_dump() for p in payload.ports]

    if payload.env is not None:
        service.env = payload.env

    if payload.resources is not None:
        service.resources = payload.resources.model_dump()

    service.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(service)
    return service


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(
        Service.id == service_id,
        Service.deleted_at.is_(None)
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Not found")

    service.deleted_at = datetime.utcnow()
    db.commit()
    return None
