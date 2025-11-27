# app/schemas/project.py
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field, validator


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del proyecto")
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Descripción corta del proyecto",
    )
    labels: Dict[str, str] = Field(
        default_factory=dict,
        description="Etiquetas tipo clave:valor (env, owner, etc.)",
    )

    @validator("name")
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name is required")
        return v.strip()

    @validator("labels")
    def labels_keys_values_are_strings(cls, v: Dict[str, str]) -> Dict[str, str]:
        """
        Forzamos que las llaves sean strings y los valores se conviertan a string.
        Útil por si alguien manda ints/bools en JSON.
        """
        coerced: Dict[str, str] = {}
        for k, val in v.items():
            if not isinstance(k, str):
                raise ValueError("label keys must be strings")
            coerced[k] = str(val)
        return coerced


class ProjectCreate(ProjectBase):
    """Esquema de entrada para crear un Project."""
    pass


class ProjectUpdate(BaseModel):
    """Esquema de entrada para actualizar parcialmente un Project."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    labels: Optional[Dict[str, str]] = None

    @validator("name")
    def name_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("name cannot be blank")
        return v.strip() if v else v

    @validator("labels")
    def labels_keys_values_are_strings(cls, v: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        if v is None:
            return v
        coerced: Dict[str, str] = {}
        for k, val in v.items():
            if not isinstance(k, str):
                raise ValueError("label keys must be strings")
            coerced[k] = str(val)
        return coerced


class ProjectRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    labels: Dict[str, str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
