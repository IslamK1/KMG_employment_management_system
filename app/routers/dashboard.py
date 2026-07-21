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

from app import cache
from app.database import get_db
from app.dependencies import get_policy, require_auth, require_role
from app.services import (
    get_kpis,
    get_oil_dynamics,
    get_top_companies,
    get_water_cut_by_company,
    get_well_types_distribution,
)

router = APIRouter(
    prefix="/dashboard",
    dependencies=[Depends(require_auth), Depends(require_role("admin", "manager"))],
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
    request: Request,
    db: Session = Depends(get_db),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """JSON: динамика добычи нефти по датам."""
    company_id = get_policy(request).visible_company_id()
    key = f"oil-dynamics:{company_id}:{date_from}:{date_to}"
    data = cache.get_or_set(
        key, lambda: get_oil_dynamics(db, date_from, date_to, company_id)
    )
    return JSONResponse(data)


@router.get("/api/water-cut")
def api_water_cut(
    request: Request,
    db: Session = Depends(get_db),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """JSON: обводненность скважин одной компании."""
    company_id = get_policy(request).visible_company_id()
    key = f"water-cut:{company_id}:{date_from}:{date_to}"
    data = cache.get_or_set(
        key, lambda: get_water_cut_by_company(db, date_from, date_to, company_id)
    )
    return JSONResponse(data)


@router.get("/api/well-types")
def api_well_types(
    request: Request,
    db: Session = Depends(get_db),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """JSON: распределение фонда скважин по типам."""
    company_id = get_policy(request).visible_company_id()
    key = f"well-types:{company_id}:{date_from}:{date_to}"
    data = cache.get_or_set(
        key, lambda: get_well_types_distribution(db, date_from, date_to, company_id)
    )
    return JSONResponse(data)


@router.get("/api/top-companies")
def api_top_companies(
    request: Request,
    db: Session = Depends(get_db),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """JSON: топ компаний по добыче."""
    company_id = get_policy(request).visible_company_id()
    key = f"top-companies:{company_id}:{date_from}:{date_to}"
    data = cache.get_or_set(
        key, lambda: get_top_companies(db, date_from, date_to, company_id=company_id)
    )
    return JSONResponse(data)


@router.get("/api/kpis")
def api_kpis(
    request: Request,
    db: Session = Depends(get_db),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
):
    """JSON: ключевые показатели для карточек."""
    company_id = get_policy(request).visible_company_id()
    key = f"kpis:{company_id}:{date_from}:{date_to}"
    data = cache.get_or_set(key, lambda: get_kpis(db, date_from, date_to, company_id))
    return JSONResponse(data)
