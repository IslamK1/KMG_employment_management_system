"""
Пакет маршрутов приложения.
"""

from app.routers.auth import router as auth_router
from app.routers.daily_productions import router as productions_router
from app.routers.employees import router as emp_router
from app.routers.dashboard import router as dashboard_router

__all__ = ["auth_router", "emp_router", "productions_router", "dashboard_router"]
