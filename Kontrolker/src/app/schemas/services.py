# src_app/schemas/services.py
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class Port(BaseModel):
    host: int = Field(..., ge=1, le=65535)
    container: int = Field(..., ge=1, le=65535)


class Resources(BaseModel):
    cpu: float = Field(..., ge=0.1, le=4.0)
    memory_mb: int = Field(..., ge=64, le=8192)


class ServiceBase(BaseModel):
    project_id: int
    name: str = Field(..., min_length=2, max_length=100)
    image: str = Field(..., min_length=1)
    ports: List[Port] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    resources: Optional[Resources] = None

    @validator("ports")
    def no_duplicate_host_ports(cls, ports):
        hosts = [p.host for p in ports]
        if len(hosts) != len(set(hosts)):
            raise ValueError("Host port duplicated")
        return ports


class ServiceCreate(ServiceBase):
    """Lo que entra en POST /services"""
    pass


class ServiceUpdate(BaseModel):
    """Lo que entra en PATCH /services/{id}"""
    project_id: Optional[int] = None
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    image: Optional[str] = None
    ports: Optional[List[Port]] = None
    env: Optional[Dict[str, str]] = None
    resources: Optional[Resources] = None


class ServiceRead(ServiceBase):
    """Lo que sale en las respuestas"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
