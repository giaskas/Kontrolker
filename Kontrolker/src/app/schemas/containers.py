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
    ports: Dict[str, int] = Field(default_factory=dict)
    env: Dict[str, str] = Field(default_factory=dict)
    cpu: Optional[float] = None
    memory_mb: Optional[int] = None
    mounts: List[Tuple[str, str]] = Field(default_factory=list)

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
    cli_hint: Optional[str] = None  # 👈 para DX (no se persiste)

    class Config:
        from_attributes = True
