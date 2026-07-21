"""
Фоновая задача формирования Excel-отчёта по скважинам.

Тяжёлая выгрузка (сводка или детальный отчёт за месяц) считается
Celery-воркером в отдельном процессе, чтобы интерфейс не ждал. Готовый
.xlsx сохраняется во временную папку, а задача возвращает имя файла —
по нему страница потом предложит скачивание.
"""

import os
import uuid

from app.celery_app import celery_app
from app.database import SessionLocal
from app.services.excel_service import (
    export_detailed_reports,
    export_monthly_summary,
)

# папка для готовых отчётов (та же, что для загрузок — временное хранилище)
EXPORT_DIR = "uploads_tmp"


@celery_app.task(name="export_reports", bind=True)
def export_reports_job(
    self, year: int, month: int, kind: str, company_id: int | None = None
) -> dict:
    """
    Формирует Excel-отчёт в фоне и сохраняет его на диск.

    Args:
        year (int): Год.
        month (int): Месяц (1-12).
        kind (str): "summary" — сводка, "detailed" — детальный список.
        company_id (int | None): Ограничение по компании (manager видит свою).

    Returns:
        dict: {"filename": str} — имя готового файла в EXPORT_DIR,
              по которому роут отдаст его на скачивание.
    """
    os.makedirs(EXPORT_DIR, exist_ok=True)

    db = SessionLocal()
    try:
        if kind == "detailed":
            content = export_detailed_reports(db, year, month, company_id)
            prefix = "reports"
        else:
            content = export_monthly_summary(db, year, month, company_id)
            prefix = "summary"

        # уникальное имя, чтобы отчёты разных пользователей не пересекались
        filename = f"{prefix}_{year}_{month:02d}_{uuid.uuid4().hex[:8]}.xlsx"
        path = os.path.join(EXPORT_DIR, filename)
        with open(path, "wb") as f:
            f.write(content)

        return {"filename": filename}
    finally:
        db.close()
