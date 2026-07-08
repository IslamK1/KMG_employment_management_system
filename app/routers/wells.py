"""
Маршруты для управления скважинами.
Роутер принимает запросы и делегирует логику в well_service.
Авторизация проверяется автоматически через Depends(require_auth).
"""

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_auth, require_role
from app.services import (
    create_well,
    delete_well,
    get_all_companies,
    get_well_by_id,
    get_wells_paginated,
    update_well,
)

router = APIRouter(prefix="/wells", dependencies=[Depends(require_auth), Depends(require_role("admin", "manager"))])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
):
    """Список всех скважин с пагинацией."""
    wells, total = get_wells_paginated(db, page, per_page)
    total_pages = (total + per_page - 1) // per_page

    return templates.TemplateResponse(
        request=request,
        name="wells/index.html",
        context={
            "wells": wells,
            "user": request.session.get("user_name"),
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
        },
    )


@router.get("/create", response_class=HTMLResponse)
def create_form(request: Request, db: Session = Depends(get_db)):
    """Форма создания новой скважины."""
    return templates.TemplateResponse(
        request=request,
        name="wells/create.html",
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
    type: str = Form(...),
    max_drilling_depth: int = Form(...),
    oil_company_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """Создание новой скважины."""
    create_well(db, name, type, max_drilling_depth, oil_company_id)
    return RedirectResponse(url="/wells/", status_code=302)


@router.get("/edit/{well_id}", response_class=HTMLResponse)
def edit_form(well_id: int, request: Request, db: Session = Depends(get_db)):
    """Форма редактирования скважины."""
    well = get_well_by_id(db, well_id)
    if not well:
        return RedirectResponse(url="/wells/", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="wells/edit.html",
        context={
            "well": well,
            "error": None,
            "user": request.session.get("user_name"),
            "companies": get_all_companies(db),
        },
    )


@router.post("/edit/{well_id}")
def edit(
    well_id: int,
    request: Request,
    name: str = Form(...),
    type: str = Form(...),
    max_drilling_depth: int = Form(...),
    oil_company_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """Обновление данных скважины."""
    well = update_well(db, well_id, name, type, max_drilling_depth, oil_company_id)
    if not well:
        return RedirectResponse(url="/wells/", status_code=302)
    return RedirectResponse(url=f"/wells/{well_id}", status_code=302)


@router.get("/delete/{well_id}")
def delete(well_id: int, request: Request, db: Session = Depends(get_db)):
    """Удаление скважины."""
    delete_well(db, well_id)
    return RedirectResponse(url="/wells/", status_code=302)


@router.get("/{well_id}", response_class=HTMLResponse)
def show(well_id: int, request: Request, db: Session = Depends(get_db)):
    """Просмотр скважины со списком её суточных рапортов."""
    well = get_well_by_id(db, well_id)
    if not well:
        return RedirectResponse(url="/wells/", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="wells/show.html",
        context={"well": well, "user": request.session.get("user_name")},
    )
