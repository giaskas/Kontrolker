# src_app/schemas/project.py
from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    labels: Dict[str, str] = Field(default_factory=dict)


class ProjectCreate(ProjectBase):
    """Lo que entra en POST /projects"""
    pass


class ProjectUpdate(BaseModel):
    """Lo que entra en PATCH /projects/{id}"""
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    description: Optional[str] = None
    labels: Optional[Dict[str, str]] = None


class ProjectRead(ProjectBase):
    """Lo que sale en las respuestas"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
