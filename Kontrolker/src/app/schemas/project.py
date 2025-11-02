# app/schemas/projects.py
from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    # dict[str, str] en Python 3.9+ → aquí lo pongo así para que se entienda
    labels: Dict[str, str] = Field(default_factory=dict)


class ProjectCreate(ProjectBase):
    """
    Lo que el cliente MANDA cuando crea un proyecto.
    No incluimos id, ni created_at, ni updated_at porque los pone el servidor.
    """
    pass


class ProjectUpdate(BaseModel):
    """
    Lo que el cliente MANDA cuando quiere modificar un proyecto.
    Aquí TODO es opcional porque el usuario puede mandar solo un campo.
    Esto sirve para PATCH.
    """
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = None
    labels: Optional[Dict[str, str]] = None


class ProjectRead(ProjectBase):
    """
    Lo que el servidor DEVUELVE.
    Aquí sí van id y timestamps.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        # si luego usas SQLAlchemy/SQLModel, esto deja mapear desde el modelo ORM
        from_attributes = True
