# app/schemas/service.py
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator



class PortMapping(BaseModel):
    host: int
    container: int

    @validator("host", "container")
    def port_in_valid_range(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("port must be between 1 and 65535")
        return v


class ResourceSpec(BaseModel):
    cpu: float = Field(..., description="CPU cores (0.1 - 4.0)")
    memory_mb: int = Field(..., description="Memory in MB (64 - 8192)")

    @validator("cpu")
    def cpu_range(cls, v: float) -> float:
        if not 0.1 <= v <= 4.0:
            raise ValueError("cpu must be between 0.1 and 4.0")
        return v

    @validator("memory_mb")
    def memory_range(cls, v: int) -> int:
        if not 64 <= v <= 8192:
            raise ValueError("memory_mb must be between 64 and 8192")
        return v


# --- Base ---

class ServiceBase(BaseModel):
    project_id: int = Field(..., description="ID del Project dueño del servicio")
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del servicio")
    image: str = Field(..., min_length=1, description="Imagen Docker a usar (p.ej. postgres:16)")
    ports: List[PortMapping] = Field(default_factory=list, description="Mapeo de puertos host/container")
    env: Dict[str, str] = Field(default_factory=dict, description="Variables de entorno")
    resources: Optional[ResourceSpec] = Field(
        default=None,
        description="Límites de recursos (CPU y memoria)",
    )

    @validator("image")
    def image_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("image is required")
        return v.strip()

    @validator("env")
    def env_keys_values_are_strings(cls, v: Dict[str, str]) -> Dict[str, str]:
        # Forzamos a string, por si mandan int/bool
        coerced: Dict[str, str] = {}
        for k, val in v.items():
            if not isinstance(k, str):
                raise ValueError("env keys must be strings")
            coerced[k] = str(val)
        return coerced

    @validator("ports")
    def host_ports_unique(cls, v: List[PortMapping]) -> List[PortMapping]:
        hosts = [p.host for p in v]
        if len(hosts) != len(set(hosts)):
            raise ValueError("Host port duplicated within service")
        return v


# --- Esquemas de entrada/salida ---

class ServiceCreate(ServiceBase):
    """Esquema para crear un Service."""
    pass


class ServiceUpdate(BaseModel):
    """Esquema para actualizar parcialmente un Service."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    image: Optional[str] = Field(default=None, min_length=1)
    ports: Optional[List[PortMapping]] = None
    env: Optional[Dict[str, str]] = None
    resources: Optional[ResourceSpec] = None

    @validator("image")
    def image_not_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("image cannot be blank")
        return v.strip() if v else v

    @validator("env")
    def env_keys_values_are_strings(cls, v: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        if v is None:
            return v
        coerced: Dict[str, str] = {}
        for k, val in v.items():
            if not isinstance(k, str):
                raise ValueError("env keys must be strings")
            coerced[k] = str(val)
        return coerced

    @validator("ports")
    def host_ports_unique(cls, v: Optional[List[PortMapping]]) -> Optional[List[PortMapping]]:
        if v is None:
            return v
        hosts = [p.host for p in v]
        if len(hosts) != len(set(hosts)):
            raise ValueError("Host port duplicated within service")
        return v


class ServiceRead(BaseModel):
    id: int
    project_id: int
    name: str
    image: str
    ports: List[PortMapping]
    env: Dict[str, str]
    resources: Optional[ResourceSpec]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
