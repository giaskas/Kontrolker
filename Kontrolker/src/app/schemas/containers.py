# src/app/schemas/containers.py
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

class ContainerCreateFromService(BaseModel):
    service_id: int

class ContainerCreateInline(BaseModel):
    project_id: Optional[int] = None
    service_id: Optional[int] = None
    name: Optional[str] = None
    image: str
    # {"80/tcp": 8080, "5432/tcp": 5432}
    ports: Dict[str, int] = Field(default_factory=dict)
    env: Dict[str, str] = Field(default_factory=dict)
    cpu: Optional[float] = None
    memory_mb: Optional[int] = None
    mounts: List[Tuple[str, str]] = Field(default_factory=list)  # (host, container)

class ContainerRead(BaseModel):
    id: int
    docker_id: str
    name: str
    image: str
    status: str
    project_id: Optional[int]
    service_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
