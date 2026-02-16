from .chapters import router as chapters_router
from .export import router as export_router
from .health import router as health_router
from .novels import router as novels_router

all_routers = [health_router, novels_router, chapters_router, export_router]
