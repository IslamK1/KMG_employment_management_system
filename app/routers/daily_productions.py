"""
Маршруты для управления суточными производственными рапортами.
"""

from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_auth
from app.schemas import DailyProductionCreate
from app.services import (
    create_report,
    delete_report,
    get_all_reports,
    get_all_wells,
    get_report_by_id,
)

router = APIRouter(
    prefix="/productions",
    dependencies=[Depends(require_auth)],
)
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    """Сводная таблица всех суточных рапортов."""
    reports = get_all_reports(db)
    return templates.TemplateResponse(
        request=request,
        name="productions/index.html",
        context={
            "reports": reports,
            "user": request.session.get("user_name"),
        },
    )


@router.get("/create", response_class=HTMLResponse)
def create_form(request: Request, db: Session = Depends(get_db)):
    """Форма создания нового суточного рапорта."""
    return templates.TemplateResponse(
        request=request,
        name="productions/create.html",
        context={
            "wells": get_all_wells(db),
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
    """Удаление суточного рапорта."""
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
