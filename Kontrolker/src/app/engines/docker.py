# src/app/engines/docker.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import docker
from docker.models.containers import Container as DockerContainer
from docker.errors import APIError

# Guardrails (mínimos del MVP)
DENY_MOUNTS_PREFIXES = ["/", "/etc", "/var/run/docker.sock"]
DEFAULT_RESTART_POLICY = {"Name": "no"}  # sin restart por defecto

@dataclass
class CreateResult:
    docker_id: str
    name: str
    status: str

def _validate_mounts_safe(mounts: List[Tuple[str, str]] | None):
    if not mounts:
        return
    for host_path, _container_path in mounts:
        for bad in DENY_MOUNTS_PREFIXES:
            if host_path == bad or host_path.startswith(bad):
                raise ValueError(f"Mount path '{host_path}' is not allowed")

def _validate_privileged(privileged: bool | None):
    if privileged:
        raise ValueError("Running containers with --privileged is not allowed")

def get_client() -> docker.DockerClient:
    # Lee DOCKER_HOST/DOCKER_TLS_VERIFY si existen; si no, local por defecto
    return docker.from_env()

def create_and_start(
    *,
    image: str,
    name: Optional[str],
    ports: Dict[str, int] | None,
    env: Dict[str, str] | None,
    cpu: float | None,
    memory_mb: int | None,
    mounts: List[Tuple[str, str]] | None = None,  # (host, container)
    privileged: bool | None = None,
) -> CreateResult:
    """
    Crea y arranca un contenedor con guardrails básicos.
    ports: dict como {"80/tcp": 8080, "5432/tcp": 5432}  (container/proto -> host)
    """
    _validate_privileged(privileged)
    _validate_mounts_safe(mounts)

    client = get_client()

    # policy de recursos (muy básico; para MVP)
    host_config = client.api.create_host_config(
        port_bindings=ports or {},
        binds=[f"{h}:{c}" for (h, c) in (mounts or [])],
        privileged=False,
        mem_limit=f"{memory_mb}m" if memory_mb else None,
        nano_cpus=int(cpu * 1e9) if cpu else None,
        restart_policy=DEFAULT_RESTART_POLICY,
    )

    try:
        client.images.get(image)
    except docker.errors.ImageNotFound:
        client.images.pull(image)
        container = client.api.create_container(
            image=image,
            name=name,
            environment=env or {},
            host_config=host_config,
            detach=True,
        )
        docker_id = container.get("Id")
        client.api.start(docker_id)
        info = client.api.inspect_container(docker_id)
        status = info["State"]["Status"]
        return CreateResult(docker_id=docker_id, name=info["Name"].lstrip("/"), status=status)
    except APIError as e:
        # burbujea como ValueError para homogeneizar
        raise ValueError(str(e.explanation or e)) from e

def inspect(container_id: str) -> dict:
    client = get_client()
    return client.api.inspect_container(container_id)

def list_containers(*, all_: bool = False, filters: dict | None = None) -> List[dict]:
    client = get_client()
    # devuelve lista de dicts con info resumida
    return client.api.containers(all=all_, filters=filters or {})

def start(container_id: str):
    get_client().api.start(container_id)

def stop(container_id: str):
    get_client().api.stop(container_id)

def restart(container_id: str):
    get_client().api.restart(container_id)

def remove(container_id: str):
    get_client().api.remove_container(container_id)
