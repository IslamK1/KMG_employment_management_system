"""
Маршруты для управления нефтяными компаниями.
Роутер принимает запросы и делегирует логику в company_service.
Авторизация проверяется автоматически через Depends(require_auth).
"""

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_auth, require_role
from app.services import (
    create_company,
    delete_company,
    get_companies_paginated,
    get_company_by_id,
    update_company,
)

router = APIRouter(
    prefix="/companies",
    dependencies=[Depends(require_auth), Depends(require_role("admin"))],
)
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
):
    """Список всех компаний с пагинацией."""
    companies, total = get_companies_paginated(db, page, per_page)
    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse(
        request=request,
        name="companies/index.html",
        context={
            "companies": companies,
            "user": request.session.get("user_name"),
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
    )


@router.get("/create", response_class=HTMLResponse)
def create_form(request: Request):
    """Форма создания новой компании."""
    return templates.TemplateResponse(
        request=request,
        name="companies/create.html",
        context={"error": None, "user": request.session.get("user_name")},
    )


@router.post("/create")
def create(
    request: Request,
    name: str = Form(...),
    region: str = Form(...),
    db: Session = Depends(get_db),
):
    """Создание новой компании."""
    create_company(db, name, region)
    return RedirectResponse(url="/companies/", status_code=302)


@router.get("/edit/{company_id}", response_class=HTMLResponse)
def edit_form(company_id: int, request: Request, db: Session = Depends(get_db)):
    """Форма редактирования компании."""
    company = get_company_by_id(db, company_id)
    if not company:
        return RedirectResponse(url="/companies/", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="companies/edit.html",
        context={
            "company": company,
            "error": None,
            "user": request.session.get("user_name"),
        },
    )


@router.post("/edit/{company_id}")
def edit(
    company_id: int,
    request: Request,
    name: str = Form(...),
    region: str = Form(...),
    db: Session = Depends(get_db),
):
    """Обновление данных компании."""
    company = update_company(db, company_id, name, region)
    if not company:
        return RedirectResponse(url="/companies/", status_code=302)
    return RedirectResponse(url=f"/companies/{company_id}", status_code=302)


@router.get("/delete/{company_id}")
def delete(company_id: int, request: Request, db: Session = Depends(get_db)):
    """Удаление компании. При наличии связей — отказ с сообщением."""
    success = delete_company(db, company_id)
    if not success:
        # компания не удалена (есть скважины/сотрудники) — вернуть с ошибкой
        return RedirectResponse(
            url=f"/companies/{company_id}?error=has_links", status_code=302
        )
    return RedirectResponse(url="/companies/", status_code=302)


@router.get("/{company_id}", response_class=HTMLResponse)
def show(
    company_id: int,
    request: Request,
    db: Session = Depends(get_db),
    error: str | None = Query(None),
):
    """Просмотр компании со списком её скважин и сотрудников."""
    company = get_company_by_id(db, company_id)
    if not company:
        return RedirectResponse(url="/companies/", status_code=302)

    error_message = None
    if error == "has_links":
        error_message = (
            "Нельзя удалить компанию, пока у неё есть скважины или сотрудники. "
            "Сначала удалите или перенесите их."
        )

    return templates.TemplateResponse(
        request=request,
        name="companies/show.html",
        context={
            "company": company,
            "user": request.session.get("user_name"),
            "error": error_message,
        },
    )
