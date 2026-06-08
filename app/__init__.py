"""
Пакет маршрутов приложения.
Содержит роутеры для авторизации и управления сотрудниками.
"""

from app.routers.auth import router as auth_router
from app.routers.employees import router as emp_router

__all__ = ["auth_router", "emp_router"]
