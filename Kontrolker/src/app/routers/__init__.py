# src_app/routers/__init__.py
from .projects import router as projects_router
from .services import router as services_router

__all__ = ["projects_router", "services_router"]
