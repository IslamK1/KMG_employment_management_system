COMPOSE := docker compose

.DEFAULT_GOAL := help
.PHONY: help up down stop start build rebuild restart ps logs logs-app shell \
        migrate makemigrations admin seed data test format worker-logs \
        docs cache-keys cache-ttl cache-clear

help: ## Показать список команд
	@echo "Employee Management System — Docker"
	@echo ""
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  make %-16s %s\n", $$1, $$2}'
	@echo ""
	@echo "После 'make up' открой: http://localhost:8080 (nginx)"
	@echo "  admin@mail.ru / 12345  — учётка администратора"

# ─── Оркестрация (таск 12) ───────────────────────────────────────────

up: ## Поднять весь стек (сборка + запуск в фоне)
	$(COMPOSE) up -d --build

down: ## Остановить и удалить контейнеры
	$(COMPOSE) down

stop: ## Остановить контейнеры (без удаления)
	$(COMPOSE) stop

start: ## Запустить ранее остановленные контейнеры
	$(COMPOSE) start

build: ## Пересобрать образы
	$(COMPOSE) build

rebuild: ## Пересобрать образы с нуля (без кэша)
	$(COMPOSE) build --no-cache

restart: ## Перезапустить все сервисы
	$(COMPOSE) restart

ps: ## Показать статус сервисов
	$(COMPOSE) ps

logs: ## Логи всех сервисов (follow)
	$(COMPOSE) logs -f

logs-app: ## Логи приложения: миграции + создание админа (таск 12)
	$(COMPOSE) logs app

shell: ## Bash внутри контейнера app
	$(COMPOSE) exec app bash

migrate: ## Применить миграции Alembic
	$(COMPOSE) exec app alembic upgrade head

makemigrations: ## Создать миграцию:  make makemigrations name="описание"
	$(COMPOSE) exec app alembic revision --autogenerate -m "$(name)"

admin: ## Создать администратора (admin@mail.ru / 12345)
	$(COMPOSE) exec app python -m seeders.create_admin

seed: ## Заполнить БД тестовыми ролями (admin/manager/operator)
	$(COMPOSE) exec app python -m seeders.seed

data: ## Заполнить БД демо-данными (компании, скважины, рапорты)
	$(COMPOSE) exec app python -m seeders.seed_data

test: ## Запустить тесты (pytest) — таски 12/13/14
	$(COMPOSE) exec app pytest -v

format: ## Форматирование и линтинг (ruff)
	$(COMPOSE) exec app sh -c "ruff format . && ruff check . --fix"

worker-logs: ## Логи Celery-воркера
	$(COMPOSE) logs -f celery

# ─── Мобильное API (таск 13) ─────────────────────────────────────────

docs: ## Показать ссылку на Swagger (интерактивное API)
	@echo "Swagger UI:  http://localhost:8080/docs"
	@echo "Вход: admin@mail.ru / 12345 (кнопка Authorize)"

# ─── Кэш дашборда (таск 14) ──────────────────────────────────────────

cache-keys: ## Показать ключи кэша дашборда в Redis
	$(COMPOSE) exec redis redis-cli KEYS "dashboard:*"

cache-ttl: ## Показать TTL кэша (секунды до истечения, <= 3600)
	$(COMPOSE) exec redis redis-cli TTL "dashboard:kpis:None:None:None"

cache-clear: ## Вручную сбросить кэш дашборда (вызывает cache.invalidate)
	$(COMPOSE) exec app python -c "from app import cache; cache.invalidate(); print('Кэш дашборда сброшен')"
