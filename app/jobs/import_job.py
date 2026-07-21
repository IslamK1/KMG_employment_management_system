"""
Фоновая задача массового импорта суточных рапортов из Excel.

Аналог Laravel ImportDailyProductionsJob. Выполняется Celery-воркером
в отдельном процессе: веб-сервер не ждёт обработки и сразу отвечает
оператору, а тяжёлая работа (файл на десятки тысяч строк) идёт в фоне.
"""

import os

from app.celery_app import celery_app
from app.database import SessionLocal
from app.services.excel_service import import_productions


@celery_app.task(name="import_daily_productions", bind=True)
def import_daily_productions_job(
    self, file_path: str, company_id: int | None = None
) -> dict:
    """
    Импортирует рапорты из Excel-файла в фоне.

    Веб-процесс сохраняет загруженный файл на диск и передаёт сюда путь.
    Задача сама открывает сессию БД (у воркера нет доступа к сессии
    веб-запроса — это другой процесс) и переиспользует общий сервис
    import_productions со всей валидацией и upsert-логикой.

    Args:
        file_path (str): Путь к временно сохранённому .xlsx файлу.
        company_id (int | None): Ограничение по компании (для manager/operator).

    Returns:
        dict: {"created": int, "updated": int, "errors": [...]} —
              сохраняется в Redis как результат задачи.
    """
    db = SessionLocal()
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        result = import_productions(db, file_bytes, company_id)
        return result
    finally:
        db.close()
        # подчищаем временный файл после обработки
        if os.path.exists(file_path):
            os.remove(file_path)
