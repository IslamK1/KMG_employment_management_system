#!/bin/bash
set -e

# Скрипт выполняет подготовку только для основного веб-сервиса (app),
# который стартует командой gunicorn. Для celery/frontend — просто exec.
if [ "$1" = "gunicorn" ]; then

    # Хост и порт БД: по умолчанию сервис db из docker-compose.
    # Можно переопределить переменными окружения DB_HOST / DB_PORT.
    DB_HOST="${DB_HOST:-db}"
    DB_PORT="${DB_PORT:-5432}"

    echo "Ожидаем готовности PostgreSQL (${DB_HOST}:${DB_PORT})..."
    until nc -z "$DB_HOST" "$DB_PORT"; do
        echo "  база ещё не готова, ждём..."
        sleep 2
    done
    echo "PostgreSQL готов."

    echo "Применяем миграции Alembic..."
    alembic upgrade head

    echo "Создаём администратора (admin@mail.ru / 12345)..."
    python -m seeders.create_admin

    echo "-------------------------------------------------------"
    echo "Backend готов. Приложение запускается."
    echo "-------------------------------------------------------"
fi

# Передаём управление CMD (gunicorn / celery / npm ...)
exec "$@"
