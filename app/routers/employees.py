"""
Маршруты для управления сотрудниками.
Роутер принимает запросы и делегирует логику в employee_service.
Авторизация проверяется автоматически через Depends(require_auth).
"""

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_auth, require_role
from app.services import (
    create_employee,
    delete_employee,
    get_all_companies,
    get_employee_by_id,
    get_employees_paginated,
    set_employee_role,
    update_employee,
)

# Все маршруты защищены через require_auth автоматически
router = APIRouter(prefix="/employees", dependencies=[Depends(require_auth), Depends(require_role("admin"))])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
):
    """Список всех сотрудников с пагинацией."""
    employees, total = get_employees_paginated(db, page, per_page)
    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse(
        request=request,
        name="employees/index.html",
        context={
            "employees": employees,
            "user": request.session.get("user_name"),
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
    )


@router.get("/create", response_class=HTMLResponse)
def create_form(request: Request, db: Session = Depends(get_db)):
    """Форма создания нового сотрудника."""
    return templates.TemplateResponse(
        request=request,
        name="employees/create.html",
        context={
            "error": None,
            "user": request.session.get("user_name"),
            "companies": get_all_companies(db),
        },
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
    """Создание нового сотрудника."""
    emp = create_employee(db, name, email, position, password, oil_company_id)
    if not emp:
        return templates.TemplateResponse(
            request=request,
            name="employees/create.html",
            context={
                "error": "Email уже занят",
                "user": request.session.get("user_name"),
                "companies": get_all_companies(db),
            },
        )
    return RedirectResponse(url="/employees/", status_code=302)


@router.get("/edit/{emp_id}", response_class=HTMLResponse)
def edit_form(emp_id: int, request: Request, db: Session = Depends(get_db)):
    """Форма редактирования сотрудника."""
    emp = get_employee_by_id(db, emp_id)
    if not emp:
        return RedirectResponse(url="/employees/", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="employees/edit.html",
        context={
            "emp": emp,
            "error": None,
            "user": request.session.get("user_name"),
            "companies": get_all_companies(db),
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
    """Обновление данных сотрудника."""
    emp = update_employee(db, emp_id, name, email, position, oil_company_id)
    if not emp:
        return RedirectResponse(url="/employees/", status_code=302)
    return RedirectResponse(url=f"/employees/{emp_id}", status_code=302)


@router.get("/delete/{emp_id}")
def delete(emp_id: int, request: Request, db: Session = Depends(get_db)):
    """Удаление сотрудника."""
    delete_employee(db, emp_id)
    return RedirectResponse(url="/employees/", status_code=302)


@router.get("/{emp_id}", response_class=HTMLResponse)
def show(emp_id: int, request: Request, db: Session = Depends(get_db)):
    """Просмотр одного сотрудника."""
    emp = get_employee_by_id(db, emp_id)
    if not emp:
        return RedirectResponse(url="/employees/", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="employees/show.html",
        context={"emp": emp, "user": request.session.get("user_name")},
    )


@router.post("/set-role/{emp_id}")
def set_role(emp_id: int, role: str = Form(...), db: Session = Depends(get_db)):
    """Назначение роли сотруднику (только admin — роутер уже защищён)."""
    set_employee_role(db, emp_id, role)
    return RedirectResponse(url=f"/employees/{emp_id}", status_code=302)
