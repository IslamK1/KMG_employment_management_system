"""
Модуль авторизации.
Содержит маршруты для входа и выхода из системы.
"""

import bcrypt
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """
    Отображает страницу входа.

    Если пользователь уже залогинен — перенаправляет на список сотрудников.

    Args:
        request (Request): Объект текущего HTTP запроса.

    Returns:
        HTMLResponse | RedirectResponse: Страница входа или редирект на /employees/.
    """

    if request.session.get("user"):
        return RedirectResponse(url="/employees/", status_code=302)

    return templates.TemplateResponse(
        request=request, name="login.html", context={"error": None}
    )


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Обрабатывает форму входа.

    Проверяет email и пароль пользователя.
    При успехе создаёт сессию и перенаправляет на дашборд.
    При ошибке возвращает форму с сообщением об ошибке.

    Args:
        request (Request): Объект текущего HTTP запроса.
        email (str): Email из формы входа.
        password (str): Пароль из формы входа.
        db (Session): Сессия базы данных.

    Returns:
        HTMLResponse | RedirectResponse: Форма с ошибкой или редирект на /employees/.
    """

    employee = db.query(Employee).filter(Employee.email == email).first()

    if not employee or not bcrypt.checkpw(
        password.encode(), employee.password.encode()
    ):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Неверный email или пароль"},
        )

    request.session["user"] = employee.email
    request.session["user_name"] = employee.name

    return RedirectResponse(url="/employees/", status_code=302)


@router.get("/logout")
def logout(request: Request):
    """
    Выполняет выход из системы.

    Очищает сессию пользователя и перенаправляет на страницу входа.

    Args:
        request (Request): Объект текущего HTTP запроса.

    Returns:
        RedirectResponse: Редирект на /login.
    """

    request.session.clear()

    return RedirectResponse(url="/login", status_code=302)
