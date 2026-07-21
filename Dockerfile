FROM python:3.11-slim

# Логи сразу в stdout, без .pyc-файлов
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Системные зависимости (psycopg2-binary — готовый wheel, компилятор не нужен):
#   netcat-traditional — ждём готовности БД в entrypoint (nc -z)
#   curl               — нужен для установки Node из NodeSource
#   Node 20            — сборка Tailwind CSS (сервис frontend)
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-traditional \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /var/www

# Сначала только зависимости — этот слой кэшируется, пока requirements не менялся
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Затем весь код (в dev его перекрывает bind-mount из docker-compose,
# но образ остаётся самодостаточным — важно для celery-воркера)
COPY . .

# Entrypoint: ждёт БД, гоняет миграции, создаёт админа
COPY docker-compose/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# FastAPI = ASGI, поэтому gunicorn с uvicorn-воркером (не wsgi, как в Django)
CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3"]
