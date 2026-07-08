"""
Маршруты авторизации.
Роутер принимает запросы и делегирует логику в auth_service.
"""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import authenticate_employee

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """
    Отображает страницу входа.

    Если пользователь уже залогинен — перенаправляет на /employees/.

    Args:
        request (Request): Объект текущего HTTP запроса.

    Returns:
        HTMLResponse | RedirectResponse: Страница входа или редирект.
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

    Делегирует проверку credentials в auth_service.
    При успехе создаёт сессию и редиректит на дашборд.

    Args:
        request (Request): Объект текущего HTTP запроса.
        email (str): Email из формы входа.
        password (str): Пароль из формы входа.
        db (Session): Сессия базы данных.

    Returns:
        HTMLResponse | RedirectResponse: Форма с ошибкой или редирект на /employees/.
    """
    employee = authenticate_employee(db, email, password)
    if not employee:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Неверный email или пароль"},
        )

    request.session["user"] = employee.email
    request.session["user_name"] = employee.name
    request.session["user_role"] = employee.role
    request.session["user_company_id"] = employee.oil_company_id
    return RedirectResponse(url="/productions/", status_code=302)


@router.get("/logout")
def logout(request: Request):
    """
    Выполняет выход из системы.

    Очищает сессию и редиректит на страницу входа.

    Args:
        request (Request): Объект текущего HTTP запроса.

    Returns:
        RedirectResponse: Редирект на /login.
    """
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)
