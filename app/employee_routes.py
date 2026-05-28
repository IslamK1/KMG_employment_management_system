from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import bcrypt
from app.database import get_db
from app.models import Employee, OilCompany 
from app.dependencies import require_auth

# prefix="/employees" — все роуты в этом файле начинаются с /employees
# GET / становится GET /employees/
# GET /create становится GET /employees/create
# и так далее
router = APIRouter(prefix="/employees")

templates = Jinja2Templates(directory="templates")


# Локальный охранник — вызывается в начале каждого роута
# Проверяет залогинен ли пользователь
# Возвращает редирект если нет, None если да
def auth_guard(request: Request):
    result = require_auth(request)  # из dependencies.py

    # isinstance проверяет тип объекта
    # Если вернулся RedirectResponse — пользователь не залогинен
    if isinstance(result, RedirectResponse):
        return result  # возвращаем редирект на /login

    return None  # пользователь залогинен, всё ок


# GET /employees/ — список всех сотрудников (главная страница дашборда)
@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    # Проверяем авторизацию — если не залогинен, уходим на /login
    guard = auth_guard(request)
    if guard:
        return guard

    # Получаем всех сотрудников из БД
    # SQL: SELECT * FROM employees
    employees = db.query(Employee).all()

    # Рендерим шаблон и передаём список сотрудников
    # user — имя залогиненного пользователя для отображения в navbar
    return templates.TemplateResponse(
        request=request,
        name="employees/index.html",
        context={
            "employees": employees,
            "user": request.session.get("user_name")
        },
    )


# GET /employees/create — форма создания нового сотрудника
@router.get("/create", response_class=HTMLResponse)
def create_form(request: Request, db: Session = Depends(get_db)):
    guard = auth_guard(request)
    if guard:
        return guard
    
    companies = db.query(OilCompany).all()  # Cписок компаний для выбора в форме

    # Просто показываем пустую форму, error=None — нет ошибок
    return templates.TemplateResponse(
        request=request,
        name="employees/create.html",
        context= {"error": None, 
         "user": request.session.get("user_name")
         , "companies": companies},
    )


# POST /employees/create — сохраняем нового сотрудника в БД
@router.post("/create")
def create(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    position: str = Form(""),   
    password: str = Form(...),
    oil_company_id: int = Form(None),  
    db: Session = Depends(get_db),
):
    guard = auth_guard(request)
    if guard:
        return guard

    # Проверяем что email ещё не занят другим сотрудником
    # SQL: SELECT * FROM employees WHERE email = '...' LIMIT 1
    existing = db.query(Employee).filter(Employee.email == email).first()
    if existing:
        companies = db.query(OilCompany).all() 
        # Возвращаем форму с ошибкой — не делаем редирект
        return templates.TemplateResponse(
            request=request,
            name="employees/create.html",
            context={
                "error": "Email уже занят",
                "user": request.session.get("user_name"),
                "companies": companies 
            },
        )

    # Хэшируем пароль перед сохранением
    # gensalt() — генерирует случайную соль, делает каждый хэш уникальным
    # .encode() — строка в байты (bcrypt требует байты)
    # .decode() — байты обратно в строку для хранения в БД
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # Создаём объект сотрудника
    emp = Employee(
        name=name,
        email=email,
        position=position,
        password=hashed_password,
        oil_company_id=oil_company_id
    )

    db.add(emp)     # добавляем в сессию (ещё не в БД)
    db.commit()     # сохраняем в БД — теперь сотрудник в таблице

    # После создания отправляем на список сотрудников
    return RedirectResponse(url="/employees/", status_code=302)


# GET /employees/edit/{emp_id} — форма редактирования сотрудника
# {emp_id} — динамический параметр в URL, например /employees/edit/3
@router.get("/edit/{emp_id}", response_class=HTMLResponse)
def edit_form(emp_id: int, request: Request, db: Session = Depends(get_db)):
    guard = auth_guard(request)
    if guard:
        return guard

    # Ищем сотрудника по id
    # SQL: SELECT * FROM employees WHERE id = 3 LIMIT 1
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    companies = db.query(OilCompany).all()  
    # Если сотрудник не найден — отправляем на список (не падаем с ошибкой)
    if not emp:
        return RedirectResponse(url="/employees/", status_code=302)

    # Передаём найденного сотрудника в шаблон — форма заполнится его данными
    return templates.TemplateResponse(
        request=request,
        name="employees/edit.html",
        context={
            "emp": emp,
            "error": None,
            "user": request.session.get("user_name"),
            "companies": companies 
        },
    )


# POST /employees/edit/{emp_id} — сохраняем изменения сотрудника
@router.post("/edit/{emp_id}")
def edit(
    emp_id: int,
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    position: str = Form(""),
    oil_company_id: int = Form(None),
    db: Session = Depends(get_db),
):
    guard = auth_guard(request)
    if guard:
        return guard

    # Находим сотрудника которого редактируем
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        return RedirectResponse(url="/employees/", status_code=302)

    # Обновляем поля — SQLAlchemy отслеживает изменения объекта
    emp.name = name
    emp.email = email
    emp.position = position
    emp.oil_company_id = oil_company_id
    
    # Сохраняем изменения в БД
    db.commit()

    # После редактирования отправляем на страницу просмотра этого сотрудника
    return RedirectResponse(url=f"/employees/{emp_id}", status_code=302)


# GET /employees/delete/{emp_id} — удаляем сотрудника
@router.get("/delete/{emp_id}")
def delete(emp_id: int, request: Request, db: Session = Depends(get_db)):
    guard = auth_guard(request)
    if guard:
        return guard

    # Находим сотрудника
    emp = db.query(Employee).filter(Employee.id == emp_id).first()

    # Удаляем только если нашли (защита от повторного удаления)
    if emp:
        db.delete(emp)  # помечаем на удаление
        db.commit()     # выполняем удаление в БД

    # Возвращаемся на список
    return RedirectResponse(url="/employees/", status_code=302)


# GET /employees/{emp_id} — страница просмотра одного сотрудника
# ВАЖНО: этот роут должен быть ПОСЛЕДНИМ — иначе /edit и /delete
# будут восприниматься как {emp_id} и не будут работать
@router.get("/{emp_id}", response_class=HTMLResponse)
def show(emp_id: int, request: Request, db: Session = Depends(get_db)):
    guard = auth_guard(request)
    if guard:
        return guard

    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        return RedirectResponse(url="/employees/", status_code=302)

    return templates.TemplateResponse(
        request=request,
        name="employees/show.html",
        context={"emp": emp, "user": request.session.get("user_name")},
    )