"""
Маршруты импорта и экспорта Excel.

Импорт выполняется в фоне через Celery: роут сохраняет файл, ставит
задачу в очередь и мгновенно отвечает — интерфейс не ждёт обработки.
Страница рапортов опрашивает статус задачи и показывает результат.
Экспорт (сводка/детальный) остаётся синхронным — он быстрый.
"""

import os
import uuid
from io import BytesIO

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.database import get_db
from app.dependencies import require_auth
from app.jobs.export_job import export_reports_job
from app.jobs.import_job import import_daily_productions_job
from app.services import (
    build_import_template,
    get_all_wells,
)

router = APIRouter(prefix="/excel", dependencies=[Depends(require_auth)])

XLSX_MEDIA = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# временная папка для загруженных файлов (worker прочитает и удалит)
UPLOAD_DIR = "uploads_tmp"
os.makedirs(UPLOAD_DIR, exist_ok=True)


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
async def import_file(request: Request, file: UploadFile = File(...)):
    """
    Принимает файл и ставит задачу импорта в очередь.

    Обработка НЕ происходит здесь — файл сохраняется на диск, задача
    уходит в Redis, а оператор мгновенно возвращается на страницу
    рапортов с id задачи для отслеживания статуса.
    """
    if not file.filename.endswith(".xlsx"):
        request.session["import_result"] = {"error": "Нужен файл формата .xlsx"}
        return RedirectResponse(url="/productions/", status_code=302)

    # сохраняем файл во временную папку под уникальным именем
    content = await file.read()
    tmp_name = f"{uuid.uuid4().hex}.xlsx"
    tmp_path = os.path.join(UPLOAD_DIR, tmp_name)
    with open(tmp_path, "wb") as f:
        f.write(content)

    # кладём задачу в очередь — worker подхватит её в фоне
    task = import_daily_productions_job.delay(tmp_path)

    # мгновенный ответ: оператор видит "идёт обработка", не ждёт импорт
    return RedirectResponse(url=f"/productions/?task={task.id}", status_code=302)


@router.get("/import/status/{task_id}")
def import_status(task_id: str):
    """
    Статус фоновой задачи импорта — сюда опрашивает страница.

    PENDING — в очереди, STARTED — worker обрабатывает,
    SUCCESS — готово (+результат), FAILURE — задача упала.
    """
    result = celery_app.AsyncResult(task_id)

    if result.state == "SUCCESS":
        return JSONResponse({"state": "SUCCESS", "result": result.result})
    if result.state == "FAILURE":
        return JSONResponse({"state": "FAILURE", "error": str(result.info)})

    return JSONResponse({"state": result.state})


@router.get("/export")
def export_start(
    request: Request,
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    kind: str = Query("summary"),
):
    """
    Ставит задачу формирования отчёта в очередь и редиректит с task_id.

    Экспорт отчётов холдинга недоступен оператору.
    Сам файл здесь НЕ генерируется — этим займётся worker в фоне.
    """
    if request.session.get("user_role") == "operator":
        return RedirectResponse(url="/productions/", status_code=302)

    task = export_reports_job.delay(year, month, kind)
    return RedirectResponse(
        url=f"/productions/?export_task={task.id}", status_code=302
    )


@router.get("/export/status/{task_id}")
def export_status(task_id: str):
    """
    Статус фоновой задачи экспорта — сюда опрашивает страница.

    SUCCESS — отчёт готов (+имя файла для скачивания).
    """
    result = celery_app.AsyncResult(task_id)

    if result.state == "SUCCESS":
        return JSONResponse({"state": "SUCCESS", "result": result.result})
    if result.state == "FAILURE":
        return JSONResponse({"state": "FAILURE", "error": str(result.info)})

    return JSONResponse({"state": result.state})


@router.get("/export/download/{filename}")
def export_download(filename: str):
    """Отдаёт готовый файл отчёта на скачивание и удаляет его с диска."""
    # защита от подстановки путей: берём только имя файла, без папок
    safe_name = os.path.basename(filename)
    path = os.path.join(UPLOAD_DIR, safe_name)

    if not os.path.exists(path):
        return JSONResponse(
            {"error": "Файл не найден или уже скачан"}, status_code=404
        )

    with open(path, "rb") as f:
        content = f.read()
    os.remove(path)  # одноразовое скачивание — чистим временный файл

    return _xlsx_response(content, safe_name)
