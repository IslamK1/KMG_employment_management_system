"""
Маршруты для управления суточными производственными рапортами.
"""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_policy, require_auth
from app.policies.access_policy import REPORT_EDIT_DAYS
from app.schemas import DailyProductionCreate
from app.services import (
    create_report,
    delete_report,
    get_report_by_id,
    get_reports_paginated,
)

router = APIRouter(
    prefix="/productions",
    dependencies=[Depends(require_auth)],
)
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    task: str | None = Query(None),
    export_task: str | None = Query(None),
    error: str | None = Query(None),
):
    """Сводная таблица рапортов с пагинацией (по компании пользователя)."""
    policy = get_policy(request)
    reports, total = get_reports_paginated(
        db, page, per_page, company_id=policy.visible_company_id()
    )
    total_pages = (total + per_page - 1) // per_page

    # результат импорта Excel (если был) — забираем из сессии один раз
    import_result = request.session.pop("import_result", None)
    today = date.today()
    week_ago = today - timedelta(days=REPORT_EDIT_DAYS)

    error_message = None
    if error == "locked":
        error_message = (
            "Нельзя удалять рапорты старше недели. Обратитесь к администратору."
        )

    return templates.TemplateResponse(
        request=request,
        name="productions/index.html",
        context={
            "reports": reports,
            "user": request.session.get("user_name"),
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "import_result": import_result,
            "import_task": task,
            "export_task": export_task,
            "current_year": today.year,
            "current_month": today.month,
            "week_ago": week_ago,
            "error": error_message,
        },
    )


@router.get("/create", response_class=HTMLResponse)
def create_form(request: Request, db: Session = Depends(get_db)):
    """Форма создания нового суточного рапорта."""
    policy = get_policy(request)

    # скважины для выбора с учётом роли: admin — все,
    # manager/operator — только своей компании
    wells = policy.wells_for_form(db)

    return templates.TemplateResponse(
        request=request,
        name="productions/create.html",
        context={
            "wells": wells,
            "error": None,
            "user": request.session.get("user_name"),
            "today": date.today(),
        },
    )


@router.post("/create")
def create(
    request: Request,
    well_id: int = Form(...),
    report_date: date = Form(...),
    working_hours: float = Form(...),
    liquid_volume: float = Form(...),
    water_cut: float = Form(...),
    density: float = Form(0.86),
    db: Session = Depends(get_db),
):
    """Создание нового суточного рапорта с валидацией."""
    policy = get_policy(request)

    # проверка права вносить рапорт по этой скважине (operator — только свои)
    if not policy.can_create_report_for_well(db, well_id):
        return templates.TemplateResponse(
            request=request,
            name="productions/create.html",
            context={
                "wells": policy.wells_for_form(db),
                "error": "Можно вносить рапорты только по скважинам своей компании",
                "user": request.session.get("user_name"),
                "today": date.today(),
            },
        )

    try:
        data = DailyProductionCreate(
            well_id=well_id,
            date=report_date,
            working_hours=working_hours,
            liquid_volume=liquid_volume,
            water_cut=water_cut,
            density=density,
        )
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="productions/create.html",
            context={
                "wells": policy.wells_for_form(db),
                "error": str(e),
                "user": request.session.get("user_name"),
                "today": date.today(),
            },
        )

    report, error = create_report(db, data)
    if error:
        return templates.TemplateResponse(
            request=request,
            name="productions/create.html",
            context={
                "wells": policy.wells_for_form(db),
                "error": error,
                "user": request.session.get("user_name"),
                "today": date.today(),
            },
        )
    return RedirectResponse(url="/productions/", status_code=302)


@router.get("/delete/{report_id}")
def delete(report_id: int, request: Request, db: Session = Depends(get_db)):
    """Удаление суточного рапорта (старые рапорты защищены от всех кроме admin)."""
    policy = get_policy(request)
    report = get_report_by_id(db, report_id)

    # запрет: чужой рапорт или старше недели (для всех кроме admin)
    if not policy.can_delete_report(db, report):
        return RedirectResponse(url="/productions/?error=locked", status_code=302)

    delete_report(db, report_id)
    return RedirectResponse(url="/productions/", status_code=302)


@router.get("/{report_id}", response_class=HTMLResponse)
def show(report_id: int, request: Request, db: Session = Depends(get_db)):
    """Просмотр рапорта (только по скважине своей компании)."""
    report = get_report_by_id(db, report_id)
    if not report or not get_policy(request).can_view_report(db, report):
        return RedirectResponse(url="/productions/", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="productions/show.html",
        context={
            "report": report,
            "user": request.session.get("user_name"),
        },
    )
