# APIRouter — мини-роутер, позволяет разбить роуты по разным файлам
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import bcrypt

from app.database import get_db
from app.models import Employee

# Создаём роутер для авторизации
# Все роуты из этого файла подключаются в main.py через include_router
router = APIRouter()

# Указываем папку где лежат HTML шаблоны
# Когда пишем name="login.html" — Jinja2 ищет файл templates/login.html
templates = Jinja2Templates(directory="templates")


# GET /login — показывает страницу входа
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    # Если пользователь уже залогинен — не показываем логин, отправляем на дашборд
    if request.session.get("user"):
        return RedirectResponse(url="/employees/", status_code=302)

    # Рендерим HTML шаблон и передаём в него данные через context
    # error=None — нет ошибки при первом открытии страницы
    return templates.TemplateResponse(
        request=request, name="login.html", context={"error": None}
    )


# POST /login — обрабатывает отправку формы входа
# Form(...) — данные приходят из HTML формы, ... означает что поле обязательное
@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),       # берём email из формы
    password: str = Form(...),    # берём пароль из формы
    db: Session = Depends(get_db),  # FastAPI сам создаст сессию БД
):
    # Ищем сотрудника по email в базе данных
    # SQL: SELECT * FROM employees WHERE email = '...' LIMIT 1
    employee = db.query(Employee).filter(Employee.email == email).first()

    # Проверяем два условия:
    # 1. employee не найден (неверный email)
    # 2. пароль не совпадает с хэшем в БД
    # bcrypt.checkpw сравнивает введённый пароль с хэшем безопасно
    # .encode() — переводим строку в байты, bcrypt работает только с байтами
    if not employee or not bcrypt.checkpw(password.encode(), employee.password.encode()):
        # Возвращаем форму логина с сообщением об ошибке
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Неверный email или пароль"},
        )

    # Всё ок — сохраняем данные пользователя в сессию
    # Сессия хранится в зашифрованной cookie в браузере
    request.session["user"] = employee.email       # для проверки авторизации
    request.session["user_name"] = employee.name   # для отображения в navbar

    # Отправляем на список сотрудников
    return RedirectResponse(url="/employees/", status_code=302)


# GET /logout — выход из системы
@router.get("/logout")
def logout(request: Request):
    # Полностью очищаем сессию — после этого пользователь считается незалогиненным
    request.session.clear()

    # Отправляем на страницу входа
    return RedirectResponse(url="/login", status_code=302)