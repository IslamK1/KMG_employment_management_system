"""
Точка входа приложения Employee Management System.

Настраивает FastAPI приложение, подключает middleware сессий,
статические файлы и роутеры авторизации и сотрудников.
"""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.routers import auth_router, emp_router

app = FastAPI(title="Employee Management System")

app.add_middleware(
    SessionMiddleware,
    secret_key="a3f8e2c1b9d4f7a6e5c2b8d1f4a7e3c6b9d2f5a8e1c4b7d0f3a6e9c2b5d8f1",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(emp_router)


@app.get("/")
def root():
    """
    Корневой маршрут приложения.

    Перенаправляет пользователя с главной страницы на список сотрудников.
    Если пользователь не залогинен — будет автоматически перенаправлен
    на страницу входа через middleware авторизации.

    Returns:
        RedirectResponse: Редирект на /employees/.
    """

    return RedirectResponse(url="/employees/")
