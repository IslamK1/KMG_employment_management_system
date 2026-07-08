"""
Конфигурация Celery — системы фоновых задач.

Celery состоит из двух частей:
  1. Клиент (в веб-приложении): кладёт задачи в очередь через .delay().
  2. Worker (отдельный процесс): берёт задачи из очереди и выполняет.

Очередь и результаты живут в Redis (broker и backend).
"""

import os

from celery import Celery
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "ems",  # имя приложения
    broker=REDIS_URL,  # откуда worker берёт задачи
    backend=REDIS_URL,  # куда складываются результаты выполнения
    include=["app.jobs.import_job", "app.jobs.export_job"],  # модули с задачами
)

celery_app.conf.update(
    task_track_started=True,  # показывать статус STARTED во время выполнения
    result_expires=3600,  # результаты хранятся 1 час, потом чистятся
)
