# src_app/routers/projects.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status, Depends
from sqlalchemy.orm import Session

from app.schemas import ProjectCreate, ProjectRead, ProjectUpdate
from app.db.deps import get_db
from app.models.project import Project

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    # 1) validar nombre único
    existing = db.query(Project).filter(
        Project.name == payload.name,
        Project.deleted_at.is_(None)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Project name must be unique")

    now = datetime.utcnow()
    project = Project(
        name=payload.name,
        description=payload.description,
        labels=payload.labels,
        created_at=now,
        updated_at=now,
        deleted_at=None,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get(
    "/read",
    response_model=List[ProjectRead],
)
def list_projects(
    label: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Project).filter(Project.deleted_at.is_(None))

    if label:
        # label = "env=prod"
        if "=" not in label:
            raise HTTPException(status_code=422, detail="Label filter must be in form key=value")
        key, value = label.split("=", 1)
        # en SQLite con JSON se puede hacer más pro, pero para MVP:
        projects = query.all()
        return [
            p for p in projects
            if p.labels and p.labels.get(key) == value
        ]
    return query.all()


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.deleted_at.is_(None)
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Not found")
    return project


@router.patch(
    "/{project_id}",
    response_model=ProjectRead,
)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.deleted_at.is_(None)
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Not found")

    # si viene name, validar unicidad
    if payload.name is not None:
        exists = db.query(Project).filter(
            Project.id != project_id,
            Project.name == payload.name,
            Project.deleted_at.is_(None),
        ).first()
        if exists:
            raise HTTPException(status_code=409, detail="Project name must be unique")
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
)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.deleted_at.is_(None)
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Not found")

    project.deleted_at = datetime.utcnow()
    db.commit()
    return None
