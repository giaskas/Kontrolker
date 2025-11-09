# src/app/routers/containers.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.containers import Container
from app.models.service import Service
from app.models.project import Project
from app.schemas import (
    ContainerCreateFromService,
    ContainerCreateInline,
    ContainerRead,
)
from app.engines import docker as dk

router = APIRouter(
    prefix="/containers",
    tags=["Containers"],
)

def _ensure_project_exists(db: Session, project_id: int):
    exists = db.query(Project).filter(Project.id == project_id, Project.deleted_at.is_(None)).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Project not found")

def _ensure_service_exists(db: Session, service_id: int) -> Service:
    svc = db.query(Service).filter(Service.id == service_id, Service.deleted_at.is_(None)).first()
    if not svc:
        raise HTTPException(status_code=404, detail="Service not found")
    return svc

@router.post(
    "",
    response_model=ContainerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear y arrancar contenedor (desde service_id o spec inline)"
)
def create_container(
    body: ContainerCreateFromService | ContainerCreateInline,
    db: Session = Depends(get_db),
):
    # A) desde service_id
    if isinstance(body, ContainerCreateFromService) or getattr(body, "service_id", None):
        service_id = getattr(body, "service_id", None) or body.service_id
        svc = _ensure_service_exists(db, service_id)
        # mapeo de puertos: list[{host, container}] -> {"<container>/tcp": host}
        ports_map = {f'{p["container"]}/tcp': p["host"] for p in (svc.ports or [])}
        try:
            res = dk.create_and_start(
                image=svc.image,
                name=None,
                ports=ports_map,
                env=svc.env or {},
                cpu=(svc.resources or {}).get("cpu") if svc.resources else None,
                memory_mb=(svc.resources or {}).get("memory_mb") if svc.resources else None,
                mounts=None,
                privileged=False,
            )
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

        now = datetime.utcnow()
        row = Container(
            docker_id=res.docker_id,
            name=res.name,
            image=svc.image,
            status=res.status,
            project_id=svc.project_id,
            service_id=svc.id,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    # B) spec inline
    inline: ContainerCreateInline = body  # type: ignore
    if inline.project_id:
        _ensure_project_exists(db, inline.project_id)

    # Guardrails: require ports explícitos si hay exposición (tu política MVP)
    if not inline.ports:
        # Permitimos 0 puertos si el user no necesita exponer nada públicamente.
        pass

    try:
        res = dk.create_and_start(
            image=inline.image,
            name=inline.name,
            ports=inline.ports or {},
            env=inline.env or {},
            cpu=inline.cpu,
            memory_mb=inline.memory_mb,
            mounts=inline.mounts or [],
            privileged=False,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    now = datetime.utcnow()
    row = Container(
        docker_id=res.docker_id,
        name=res.name,
        image=inline.image,
        status=res.status,
        project_id=inline.project_id,
        service_id=inline.service_id,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get(
    "",
    response_model=List[ContainerRead],
    summary="Listar contenedores (filtros: project_id, service_id, status)"
)
def list_containers(
    project_id: Optional[int] = Query(default=None),
    service_id: Optional[int] = Query(default=None),
    status_: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    q = db.query(Container).filter(Container.deleted_at.is_(None))
    if project_id is not None:
        q = q.filter(Container.project_id == project_id)
    if service_id is not None:
        q = q.filter(Container.service_id == service_id)
    if status_ is not None:
        q = q.filter(Container.status == status_)
    return q.all()


@router.get(
    "/{container_id}",
    response_model=ContainerRead,
    summary="Inspeccionar contenedor (desde DB + refresco de estado en Docker)"
)
def inspect_container(container_id: int, db: Session = Depends(get_db)):
    row = db.query(Container).filter(Container.id == container_id, Container.deleted_at.is_(None)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    try:
        info = dk.inspect(row.docker_id)
        row.status = info["State"]["Status"]
        row.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(row)
    except Exception:
        # si Docker no lo encuentra, devolvemos el estado guardado
        pass
    return row


@router.post("/{container_id}/start", response_model=ContainerRead, summary="Start")
def start_container(container_id: int, db: Session = Depends(get_db)):
    row = db.query(Container).filter(Container.id == container_id, Container.deleted_at.is_(None)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    dk.start(row.docker_id)
    row.status = "running"
    row.updated_at = datetime.utcnow()
    db.commit(); db.refresh(row)
    return row


@router.post("/{container_id}/stop", response_model=ContainerRead, summary="Stop")
def stop_container(container_id: int, db: Session = Depends(get_db)):
    row = db.query(Container).filter(Container.id == container_id, Container.deleted_at.is_(None)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    dk.stop(row.docker_id)
    row.status = "exited"
    row.updated_at = datetime.utcnow()
    db.commit(); db.refresh(row)
    return row


@router.post("/{container_id}/restart", response_model=ContainerRead, summary="Restart")
def restart_container(container_id: int, db: Session = Depends(get_db)):
    row = db.query(Container).filter(Container.id == container_id, Container.deleted_at.is_(None)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    dk.restart(row.docker_id)
    row.status = "running"
    row.updated_at = datetime.utcnow()
    db.commit(); db.refresh(row)
    return row


@router.delete("/{container_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar (solo detenido)")
def delete_container(container_id: int, db: Session = Depends(get_db)):
    row = db.query(Container).filter(Container.id == container_id, Container.deleted_at.is_(None)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")

    # opcional: validar que no esté "running"
    if row.status == "running":
        raise HTTPException(status_code=409, detail="Container must be stopped before delete")

    dk.remove(row.docker_id)
    row.deleted_at = datetime.utcnow()
    db.commit()
    return None
