"""
Модуль маршрутов для управления сотрудниками.
Содержит CRUD операции: список, создание, просмотр, редактирование, удаление.
"""

import bcrypt
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Employee, OilCompany 
from app.dependencies import require_auth


router = APIRouter(prefix="/employees")

templates = Jinja2Templates(directory="templates")



def auth_guard(request: Request):
    """
    Проверяет авторизацию пользователя для защиты маршрутов.

    Вызывает require_auth и возвращает редирект если пользователь
    не залогинен. Используется в начале каждого защищённого маршрута.

    Args:
        request (Request): Объект текущего HTTP запроса.

    Returns:
        RedirectResponse | None: Редирект на /login или None если залогинен.
    """

    result = require_auth(request)  

    if isinstance(result, RedirectResponse):
        return result  

    return None 


@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    """
    Отображает список всех сотрудников.

    Args:
        request (Request): Объект текущего HTTP запроса.
        db (Session): Сессия базы данных.

    Returns:
        HTMLResponse | RedirectResponse: Страница со списком сотрудников
        или редирект на /login если не залогинен.
    """

    guard = auth_guard(request)
    if guard:
        return guard

    employees = db.query(Employee).all()

    return templates.TemplateResponse(
        request=request,
        name="employees/index.html",
        context={
            "employees": employees,
            "user": request.session.get("user_name")
        },
    )


@router.get("/create", response_class=HTMLResponse)
def create_form(request: Request, db: Session = Depends(get_db)):
    """
    Отображает форму создания нового сотрудника.

    Args:
        request (Request): Объект текущего HTTP запроса.
        db (Session): Сессия базы данных.

    Returns:
        HTMLResponse | RedirectResponse: Форма создания сотрудника
        или редирект на /login если не залогинен.
    """
     
    guard = auth_guard(request)
    if guard:
        return guard
    
    companies = db.query(OilCompany).all()  

    return templates.TemplateResponse(
        request=request,
        name="employees/create.html",
        context= {"error": None, 
         "user": request.session.get("user_name")
         , "companies": companies},
    )


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
    """
    Создаёт нового сотрудника в базе данных.

    Проверяет уникальность email перед созданием.
    Хэширует пароль через bcrypt перед сохранением.

    Args:
        request (Request): Объект текущего HTTP запроса.
        name (str): Имя сотрудника из формы.
        email (str): Email сотрудника из формы.
        position (str): Должность сотрудника из формы.
        password (str): Пароль сотрудника из формы.
        oil_company_id (int): ID компании из формы (необязательно).
        db (Session): Сессия базы данных.

    Returns:
        HTMLResponse | RedirectResponse: Форма с ошибкой если email занят,
        или редирект на /employees/ после успешного создания.
    """

    guard = auth_guard(request)
    if guard:
        return guard

    existing = db.query(Employee).filter(Employee.email == email).first()
    if existing:
        companies = db.query(OilCompany).all() 
        return templates.TemplateResponse(
            request=request,
            name="employees/create.html",
            context={
                "error": "Email уже занят",
                "user": request.session.get("user_name"),
                "companies": companies 
            },
        )

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    emp = Employee(
        name=name,
        email=email,
        position=position,
        password=hashed_password,
        oil_company_id=oil_company_id
    )

    db.add(emp)    
    db.commit()     

    return RedirectResponse(url="/employees/", status_code=302)


@router.get("/edit/{emp_id}", response_class=HTMLResponse)
def edit_form(emp_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Отображает форму редактирования сотрудника.

    Args:
        emp_id (int): ID сотрудника из URL.
        request (Request): Объект текущего HTTP запроса.
        db (Session): Сессия базы данных.

    Returns:
        HTMLResponse | RedirectResponse: Форма редактирования сотрудника,
        редирект на /employees/ если сотрудник не найден,
        или редирект на /login если не залогинен.
    """

    guard = auth_guard(request)
    if guard:
        return guard

    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    companies = db.query(OilCompany).all()  
    if not emp:
        return RedirectResponse(url="/employees/", status_code=302)

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
    """
    Сохраняет изменения сотрудника в базе данных.

    Args:
        emp_id (int): ID сотрудника из URL.
        request (Request): Объект текущего HTTP запроса.
        name (str): Новое имя сотрудника из формы.
        email (str): Новый email сотрудника из формы.
        position (str): Новая должность сотрудника из формы.
        oil_company_id (int): Новый ID компании из формы (необязательно).
        db (Session): Сессия базы данных.

    Returns:
        HTMLResponse | RedirectResponse: Редирект на страницу сотрудника
        после успешного обновления или редирект на /employees/ если не найден.
    """

    guard = auth_guard(request)
    if guard:
        return guard
    
    emp = db.query(Employee).filter(Employee.id == emp_id).first()
    if not emp:
        return RedirectResponse(url="/employees/", status_code=302)

    emp.name = name
    emp.email = email
    emp.position = position
    emp.oil_company_id = oil_company_id
    
    db.commit()

    return RedirectResponse(url=f"/employees/{emp_id}", status_code=302)



@router.get("/delete/{emp_id}")
def delete(emp_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Удаляет сотрудника из базы данных.

    Args:
        emp_id (int): ID сотрудника из URL.
        request (Request): Объект текущего HTTP запроса.
        db (Session): Сессия базы данных.

    Returns:
        RedirectResponse: Редирект на /employees/ после удаления.
    """

    guard = auth_guard(request)
    if guard:
        return guard

    emp = db.query(Employee).filter(Employee.id == emp_id).first()

    if emp:
        db.delete(emp)  
        db.commit()     

    return RedirectResponse(url="/employees/", status_code=302)


@router.get("/{emp_id}", response_class=HTMLResponse)
def show(emp_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Отображает страницу просмотра одного сотрудника.

    Args:
        emp_id (int): ID сотрудника из URL.
        request (Request): Объект текущего HTTP запроса.
        db (Session): Сессия базы данных.

    Returns:
        HTMLResponse | RedirectResponse: Страница сотрудника
        или редирект на /employees/ если не найден.
    """
    
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