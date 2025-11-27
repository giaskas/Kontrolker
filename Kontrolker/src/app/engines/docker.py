# src/app/engines/docker.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import time
import logging
import shlex

import docker
from docker.errors import APIError, ImageNotFound, DockerException

log = logging.getLogger("engines.docker")

# Guardrails
DENY_MOUNTS_PREFIXES = ["/", "/etc", "/var/run/docker.sock"]
DEFAULT_RESTART_POLICY = {"Name": "no"}

# Auto-pull
AUTO_PULL_RETRIES = 2
AUTO_PULL_BACKOFF_SEC = 2.0

@dataclass
class CreateResult:
    docker_id: str
    name: str
    status: str
    cli_hint: str  # 👈 nuevo

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
    return docker.from_env()

def _build_cli_hint(
    *, image: str, name: Optional[str], ports: Dict[str, int] | None,
    env: Dict[str, str] | None, cpu: float | None, memory_mb: int | None,
    mounts: List[Tuple[str, str]] | None
) -> str:
    parts = ["docker", "run", "-d"]
    if name:
        parts += ["--name", shlex.quote(name)]
    if memory_mb:
        parts += ["--memory", f"{int(memory_mb)}m"]
    if cpu:
        # docker run usa --cpus (no nanocpus)
        parts += ["--cpus", str(cpu)]
    for (h, c) in (mounts or []):
        parts += ["-v", f"{shlex.quote(h)}:{shlex.quote(c)}"]
    for k, v in (env or {}).items():
        parts += ["-e", f"{shlex.quote(k)}={shlex.quote(v)}"]
    for container_proto, host in (ports or {}).items():
        cont_port = container_proto.split("/")[0]
        parts += ["-p", f"{host}:{cont_port}"]
    parts.append(shlex.quote(image))
    return " ".join(parts)

def _ensure_image(client: docker.DockerClient, image: str):
    try:
        client.images.get(image)
        log.info("Image present: %s", image)
        return
    except ImageNotFound:
        last_err: Exception | None = None
        for attempt in range(1 + AUTO_PULL_RETRIES):
            try:
                log.info("Pulling image (attempt %s/%s): %s", attempt+1, 1+AUTO_PULL_RETRIES, image)
                client.images.pull(image)
                log.info("Image pulled: %s", image)
                return
            except (APIError, DockerException) as e:
                last_err = e
                log.error("Pull failed: %s (attempt %s)", e, attempt+1)
                time.sleep(AUTO_PULL_BACKOFF_SEC * (attempt + 1))
        raise ValueError(f"Could not pull image '{image}': {last_err}") from last_err
    except (APIError, DockerException) as e:
        raise ValueError(f"Docker error while checking image '{image}': {e}") from e

def create_and_start(
    *, image: str, name: Optional[str], ports: Dict[str, int] | None,
    env: Dict[str, str] | None, cpu: float | None, memory_mb: int | None,
    mounts: List[Tuple[str, str]] | None = None, privileged: bool | None = None,
) -> CreateResult:
    _validate_privileged(privileged)
    _validate_mounts_safe(mounts)

    client = get_client()
    started = time.time()

    _ensure_image(client, image)

    cli_hint = _build_cli_hint(
        image=image, name=name, ports=ports, env=env,
        cpu=cpu, memory_mb=memory_mb, mounts=mounts
    )

    try:
        host_config = client.api.create_host_config(
            port_bindings=ports or {},
            binds=[f"{h}:{c}" for (h, c) in (mounts or [])],
            privileged=False,
            mem_limit=f"{memory_mb}m" if memory_mb else None,
            nano_cpus=int(cpu * 1e9) if cpu else None,
            restart_policy=DEFAULT_RESTART_POLICY,
        )
        container = client.api.create_container(
            image=image, name=name, environment=env or {}, host_config=host_config, detach=True
        )
        docker_id = container.get("Id")
        client.api.start(docker_id)
        info = client.api.inspect_container(docker_id)
        status = info["State"]["Status"]

        log.info("Container created: id=%s name=%s image=%s status=%s duration=%.2fs",
                 docker_id, info["Name"].lstrip("/"), image, status, time.time()-started)
        return CreateResult(docker_id=docker_id, name=info["Name"].lstrip("/"), status=status, cli_hint=cli_hint)

    except (APIError, DockerException) as e:
        msg = getattr(e, "explanation", None) or str(e)
        log.error("Docker create/start error: %s", msg)
        raise ValueError(msg) from e

def inspect(container_id: str) -> dict:
    return get_client().api.inspect_container(container_id)

def list_containers(*, all_: bool = False, filters: dict | None = None) -> List[dict]:
    return get_client().api.containers(all=all_, filters=filters or {})

def start(container_id: str):
    get_client().api.start(container_id)
    log.info("Container started: %s", container_id)

def stop(container_id: str):
    get_client().api.stop(container_id)
    log.info("Container stopped: %s", container_id)

def restart(container_id: str):
    get_client().api.restart(container_id)
    log.info("Container restarted: %s", container_id)

def remove(container_id: str):
    get_client().api.remove_container(container_id)
    log.info("Container removed: %s", container_id)
