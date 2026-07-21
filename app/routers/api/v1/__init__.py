"""
Группа маршрутов /api/v1 — единая точка входа мобильного API.

Собирает все v1-роутеры под общим префиксом. Версионирование позволяет
менять веб независимо: мобильное приложение остаётся на стабильном /api/v1.
"""

from fastapi import APIRouter

from app.routers.api.v1 import auth, reports

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth.router)
api_v1_router.include_router(reports.router)

__all__ = ["api_v1_router"]
