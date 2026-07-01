"""
Маршруты импорта и экспорта Excel.

Скачивание шаблона, массовый импорт рапортов (создание/обновление) и
выгрузка отчётов (сводка или детальный список). Результат импорта
передаётся обратно через сессию (flash) и редирект на страницу рапортов.
"""

from io import BytesIO

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_auth
from app.services import (
    build_import_template,
    export_detailed_reports,
    export_monthly_summary,
    get_all_wells,
    import_productions,
)

router = APIRouter(prefix="/excel", dependencies=[Depends(require_auth)])

XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _xlsx_response(content: bytes, filename: str) -> StreamingResponse:
    """Оборачивает байты .xlsx в ответ со скачиванием файла."""
    return StreamingResponse(
        BytesIO(content),
        media_type=XLSX_MEDIA,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/template")
def download_template(db: Session = Depends(get_db)):
    """Скачивание шаблона для импорта со справочником скважин."""
    wells = get_all_wells(db)
    content = build_import_template(wells)
    return _xlsx_response(content, "import_template.xlsx")


@router.post("/import")
async def import_file(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Импорт рапортов из Excel. Результат кладётся в сессию, редирект на рапорты."""
    if not file.filename.endswith(".xlsx"):
        request.session["import_result"] = {"error": "Нужен файл формата .xlsx"}
        return RedirectResponse(url="/productions/", status_code=302)

    content = await file.read()
    try:
        result = import_productions(db, content)
    except Exception as e:
        result = {"error": f"Не удалось прочитать файл: {e}"}

    request.session["import_result"] = result
    return RedirectResponse(url="/productions/", status_code=302)


@router.get("/export")
def export_file(
    db: Session = Depends(get_db),
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    kind: str = Query("summary"),
):
    """
    Выгрузка отчёта по скважинам за месяц.

    kind="summary"  — сводка (итоги по скважинам).
    kind="detailed" — детальный список рапортов (можно залить обратно).
    """
    if kind == "detailed":
        content = export_detailed_reports(db, year, month)
        return _xlsx_response(content, f"reports_{year}_{month:02d}.xlsx")

    content = export_monthly_summary(db, year, month)
    return _xlsx_response(content, f"summary_{year}_{month:02d}.xlsx")
