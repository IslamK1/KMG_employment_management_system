"""
Маршруты для управления суточными производственными рапортами.
"""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_auth
from app.schemas import DailyProductionCreate
from app.services import (
    create_report,
    delete_report,
    get_all_wells,
    get_report_by_id,
    get_reports_paginated,
    get_wells_for_company,
    is_report_locked,
    well_belongs_to_company,
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
    """Сводная таблица рапортов с пагинацией."""
    reports, total = get_reports_paginated(db, page, per_page)
    total_pages = (total + per_page - 1) // per_page

    # результат импорта Excel (если был) — забираем из сессии один раз
    import_result = request.session.pop("import_result", None)
    today = date.today()
    week_ago = today - timedelta(days=7)

    error_message = None
    if error == "locked":
        error_message = (
            "Нельзя удалять рапорты старше недели. "
            "Обратитесь к администратору."
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
    user = get_current_user(request)

    # оператор выбирает только скважины своей компании,
    # admin и manager — все скважины
    if user and user["role"] == "operator" and user["company_id"]:
        wells = get_wells_for_company(db, user["company_id"])
    else:
        wells = get_all_wells(db)

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
    user = get_current_user(request)

    # оператор может создавать рапорт только по скважине своей компании
    if user and user["role"] == "operator":
        if not user["company_id"] or not well_belongs_to_company(
            db, well_id, user["company_id"]
        ):
            if user["company_id"]:
                wells = get_wells_for_company(db, user["company_id"])
            else:
                wells = []
            return templates.TemplateResponse(
                request=request,
                name="productions/create.html",
                context={
                    "wells": wells,
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
                "wells": get_all_wells(db),
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
                "wells": get_all_wells(db),
                "error": error,
                "user": request.session.get("user_name"),
                "today": date.today(),
            },
        )
    return RedirectResponse(url="/productions/", status_code=302)


@router.get("/delete/{report_id}")
def delete(report_id: int, request: Request, db: Session = Depends(get_db)):
    """Удаление суточного рапорта (старые рапорты защищены от всех кроме admin)."""
    user = get_current_user(request)
    report = get_report_by_id(db, report_id)

    if report and user and user["role"] != "admin":
        # запрет на удаление рапортов старше недели для всех кроме админа
        if is_report_locked(report.date):
            return RedirectResponse(
                url="/productions/?error=locked", status_code=302
            )

    delete_report(db, report_id)
    return RedirectResponse(url="/productions/", status_code=302)


@router.get("/{report_id}", response_class=HTMLResponse)
def show(report_id: int, request: Request, db: Session = Depends(get_db)):
    """Просмотр одного суточного рапорта."""
    report = get_report_by_id(db, report_id)
    if not report:
        return RedirectResponse(url="/productions/", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="productions/show.html",
        context={
            "report": report,
            "user": request.session.get("user_name"),
        },
    )
