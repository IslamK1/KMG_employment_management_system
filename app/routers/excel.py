"""
Маршруты импорта и экспорта Excel.

Страница с формами импорта/экспорта, скачивание шаблона,
загрузка файла рапортов и выгрузка сводного отчёта за месяц.
"""

from datetime import date

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_auth
from app.services import (
    build_import_template,
    export_monthly_summary,
    import_productions,
)

router = APIRouter(prefix="/excel", dependencies=[Depends(require_auth)])
templates = Jinja2Templates(directory="templates")

XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _xlsx_response(content: bytes, filename: str) -> StreamingResponse:
    """Оборачивает байты .xlsx в ответ со скачиванием файла."""
    from io import BytesIO

    return StreamingResponse(
        BytesIO(content),
        media_type=XLSX_MEDIA,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Страница импорта и экспорта."""
    today = date.today()
    return templates.TemplateResponse(
        request=request,
        name="excel/index.html",
        context={
            "user": request.session.get("user_name"),
            "result": None,
            "current_year": today.year,
            "current_month": today.month,
        },
    )


@router.get("/template")
def download_template(db: Session = Depends(get_db)):
    """Скачивание шаблона для импорта со справочником скважин."""
    from app.services import get_all_wells

    wells = get_all_wells(db)
    content = build_import_template(wells)
    return _xlsx_response(content, "import_template.xlsx")


@router.post("/import", response_class=HTMLResponse)
async def import_file(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Загрузка и массовый импорт рапортов из Excel."""
    today = date.today()

    if not file.filename.endswith(".xlsx"):
        return templates.TemplateResponse(
            request=request,
            name="excel/index.html",
            context={
                "user": request.session.get("user_name"),
                "result": {"error": "Нужен файл формата .xlsx"},
                "current_year": today.year,
                "current_month": today.month,
            },
        )

    content = await file.read()
    try:
        result = import_productions(db, content)
    except Exception as e:
        result = {"error": f"Не удалось прочитать файл: {e}"}

    return templates.TemplateResponse(
        request=request,
        name="excel/index.html",
        context={
            "user": request.session.get("user_name"),
            "result": result,
            "current_year": today.year,
            "current_month": today.month,
        },
    )


@router.get("/export")
def export_file(
    db: Session = Depends(get_db),
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
):
    """Выгрузка сводного отчёта по скважинам за месяц."""
    content = export_monthly_summary(db, year, month)
    return _xlsx_response(content, f"summary_{year}_{month:02d}.xlsx")
