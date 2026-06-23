"""
Маршруты дашборда руководства.

Отдаёт HTML-страницу дашборда и JSON-данные для графиков Chart.js.
Все графики поддерживают фильтрацию по диапазону дат.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_auth
from app.services import (
    get_kpis,
    get_oil_dynamics,
    get_top_companies,
    get_water_cut_by_company,
    get_well_types_distribution,
)

router = APIRouter(
    prefix="/dashboard",
    dependencies=[Depends(require_auth)],
)
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Главная страница дашборда с графиками."""
    return templates.TemplateResponse(
        request=request,
        name="dashboard/index.html",
        context={"user": request.session.get("user_name")},
    )


@router.get("/api/oil-dynamics")
def api_oil_dynamics(
    db: Session = Depends(get_db),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """JSON: динамика добычи нефти по датам."""
    return JSONResponse(get_oil_dynamics(db, date_from, date_to))


@router.get("/api/water-cut")
def api_water_cut(
    db: Session = Depends(get_db),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """JSON: обводненность скважин одной компании."""
    return JSONResponse(get_water_cut_by_company(db, date_from, date_to))


@router.get("/api/well-types")
def api_well_types(
    db: Session = Depends(get_db),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """JSON: распределение фонда скважин по типам."""
    return JSONResponse(get_well_types_distribution(db, date_from, date_to))


@router.get("/api/top-companies")
def api_top_companies(
    db: Session = Depends(get_db),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """JSON: топ компаний по добыче."""
    return JSONResponse(get_top_companies(db, date_from, date_to))


@router.get("/api/kpis")
def api_kpis(
    db: Session = Depends(get_db),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """JSON: ключевые показатели для карточек."""
    return JSONResponse(get_kpis(db, date_from, date_to))
