# Employee Management System

Веб-приложение для управления сотрудниками нефтяных компаний: учёт суточной добычи по скважинам, дашборд аналитики, импорт/экспорт Excel с фоновой обработкой и ролевая модель доступа (Admin / Manager / Operator).

---

## Стек технологий

- **FastAPI** — веб-фреймворк
- **SQLAlchemy** — ORM
- **Alembic** — миграции базы данных
- **PostgreSQL** — база данных
- **Jinja2** — HTML-шаблоны
- **bcrypt** — хэширование паролей
- **Starlette Sessions** — сессионная авторизация и роли
- **Faker** — генерация тестовых данных
- **TailwindCSS** — утилитарный CSS (через Tailwind CLI)
- **Chart.js** — графики на дашборде
- **openpyxl** — импорт и экспорт Excel (.xlsx)
- **Celery + Redis** — фоновая обработка тяжёлых задач
- **pytest** — тесты
- **Ruff** — линтер и форматтер (PEP-8)

---

## Функционал

- Сессионная авторизация с ролями (вход / выход)
- Ролевая модель доступа:
  - **Admin** — создаёт компании, назначает роли, полный доступ
  - **Manager (Руководитель ДЗО)** — дашборд и управление скважинами
  - **Operator (Мастер)** — вносит суточные рапорты только по скважинам своей компании
- CRUD сотрудников, компаний, скважин с детальными страницами (компания → скважины и сотрудники → рапорты)
- Суточные производственные рапорты:
  - валидация на уровне схемы и БД (время работы 0–24 ч, обводненность 0–100 %)
  - уникальное ограничение «одна скважина — один рапорт в день»
  - расчёт чистой нефти через `@property`
  - запрет редактирования рапортов старше недели (кроме Admin)
- Дашборд с 4 графиками, KPI и фильтром по датам
- Импорт рапортов из Excel (по названию скважины, режим upsert — создаёт или обновляет)
- Экспорт в Excel: сводка по скважинам или детальный список за месяц
- Фоновая обработка импорта и экспорта через Celery + Redis (интерфейс не виснет; статус обновляется на странице)
- Автоматическая генерация тестовых данных через Faker
- Тесты (pytest) для расчётов и валидации рапортов

---

## Структура проекта

    employee-management-system/
    │
    ├── app/
    │   ├── routers/                    # HTTP-маршруты (тонкий слой)
    │   │   ├── auth.py                 # вход / выход
    │   │   ├── employees.py            # сотрудники + назначение ролей (admin)
    │   │   ├── companies.py            # компании (admin)
    │   │   ├── wells.py                # скважины (admin, manager)
    │   │   ├── daily_productions.py    # суточные рапорты
    │   │   ├── dashboard.py            # дашборд + JSON API (admin, manager)
    │   │   └── excel.py                # импорт / экспорт Excel
    │   │
    │   ├── services/                   # бизнес-логика
    │   │   ├── auth_service.py
    │   │   ├── employee_service.py
    │   │   ├── company_service.py
    │   │   ├── well_service.py
    │   │   ├── daily_production_service.py
    │   │   ├── dashboard_service.py
    │   │   └── excel_service.py
    │   │
    │   ├── models/                     # модели SQLAlchemy
    │   │   ├── employee.py             # + поле role
    │   │   ├── oil_company.py
    │   │   ├── well.py
    │   │   └── daily_production.py
    │   │
    │   ├── schemas/
    │   │   └── daily_production.py     # Pydantic-валидация рапорта
    │   │
    │   ├── jobs/                       # фоновые задачи Celery
    │   │   ├── import_job.py           # импорт Excel в фоне
    │   │   └── export_job.py           # экспорт Excel в фоне
    │   │
    │   ├── main.py                     # точка входа, подключение роутеров
    │   ├── database.py                 # подключение к БД, сессии
    │   ├── dependencies.py             # авторизация и проверки ролей (Gates)
    │   └── celery_app.py               # конфигурация Celery
    │
    ├── seeders/
    │   ├── seed.py                     # учётные записи admin/manager/operator
    │   └── seed_data.py                # тестовые данные (Faker)
    │
    ├── providers/
    │   └── oil_provider.py             # кастомный Faker-провайдер
    │
    ├── migrations/                     # Alembic
    ├── templates/                      # Jinja2-шаблоны
    ├── static/                         # CSS (Tailwind), JS (Chart.js)
    ├── tests/                          # pytest
    │
    ├── Makefile
    ├── ruff.toml
    ├── alembic.ini
    ├── pytest.ini
    ├── package.json
    ├── requirements.txt
    ├── .env                            # переменные окружения (не в git)
    └── README.md

---

## Требования

- Python 3.10+
- PostgreSQL
- Node.js 18+ (сборка TailwindCSS и Chart.js)
- Redis (для фоновых задач) — через Docker или нативный сервер

---

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/IslamK1/KMG_employment_management_system.git
cd employee-management-system
```

### 2. Виртуальная среда

```bash
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```
Mac/Linux:
```bash
source .venv/Scripts/activate
```

### 3. Python-зависимости

```bash
pip install -r requirements.txt
```

### 4. Frontend-зависимости

```bash
npm install
```

### 5. Файл .env

Создайте `.env` в корне проекта:

```
DATABASE_URL=postgresql://postgres:ВАШ_ПАРОЛЬ@localhost:5432/employee_management
REDIS_URL=redis://localhost:6379/0
```

> Пароль PostgreSQL должен быть без спецсимволов URL (`#`, `@`, `:`, `/`, `?`, пробелы), иначе строка подключения ломается.

### 6. База данных

```sql
CREATE DATABASE employee_management;
```

### 7. Миграции

```bash
make migrate
```

### 8. Учётные записи

```bash
make seed
```

Создаёт трёх пользователей (пароль у всех `12345`):

| Email | Роль |
|-------|------|
| admin@mail.ru | Администратор |
| manager@mail.ru | Руководитель ДЗО |
| operator@mail.ru | Мастер |

### 9. Тестовые данные (опционально)

```bash
make data
```

### 10. Собрать стили и скрипты

```bash
make css
make js
```

### 11. Запуск

Приложению нужны **три процесса** (для фоновых задач). Каждый — в своём терминале:

```bash
# 1) Redis
make redis          # через Docker
# либо нативный сервер: redis-server (Linux/Mac) / redis-server.exe (Windows)

# 2) Celery worker
make worker

# 3) Веб-сервер
make run
```

Открыть: **http://127.0.0.1:8000**

> Redis обязателен для работы импорта/экспорта Excel. Если он не запущен, эти операции вернут ошибку подключения.

---

## Данные для входа

    Email:  admin@mail.ru
    Пароль: 12345

---

## Разработка фронтенда

Автоматическая пересборка CSS при изменении шаблонов:

```bash
make css-watch
```

---

## Команды Makefile

| Команда | Описание |
|---------|----------|
| `make run` | Запустить веб-сервер |
| `make worker` | Запустить Celery worker (фоновые задачи) |
| `make redis` | Поднять Redis в Docker |
| `make migrate` | Применить миграции |
| `make seed` | Создать учётные записи с ролями |
| `make data` | Заполнить БД тестовыми данными |
| `make css` | Собрать TailwindCSS |
| `make css-watch` | Пересобирать CSS при изменениях |
| `make js` | Скопировать Chart.js в static |
| `make test` | Запустить тесты |
| `make format` | Форматировать код через Ruff |
| `make format-check` | Проверить код без изменений |

---

## Ролевая модель

| Раздел | Admin | Manager | Operator |
|--------|:-----:|:-------:|:--------:|
| Компании | ✓ | — | — |
| Сотрудники / роли | ✓ | — | — |
| Скважины | ✓ | ✓ | — |
| Дашборд | ✓ | ✓ | — |
| Суточные рапорты | ✓ | ✓ | ✓ (только свои скважины) |
| Экспорт отчётов | ✓ | ✓ | — |
| Удаление рапортов старше недели | ✓ | — | — |

Проверки продублированы на бэкенде (зависимости-Gates в роутерах) и в шаблонах (скрытие кнопок), поэтому недоступный раздел нельзя открыть даже по прямому URL.

---

## Импорт / Экспорт Excel

Находятся на странице **Суточные рапорты**.

**Импорт.** Скачайте шаблон (лист «Скважины» содержит справочник названий), заполните рапортами, загрузите. Скважина указывается по названию (например `Скважина-13AI`). Существующий рапорт за ту же скважину и дату обновляется (upsert). Обработка идёт в фоне — на странице появляется статус, затем результат (добавлено / обновлено / ошибки по строкам).

**Экспорт.** Два типа:
- **Сводка** — итоги по скважинам за месяц (для руководства)
- **Детальный** — все рапорты построчно; формат совпадает с импортом, поэтому файл можно отредактировать и загрузить обратно

Файл формируется в фоне, по готовности появляется кнопка «Скачать».

---

## Тесты

```bash
make test
```

Покрывают расчёт чистой нефти (`@property`) и валидацию рапортов (запрет >24 часов, дубликатов) на уровне схемы, сервиса и HTTP. Используется изолированная in-memory SQLite (рабочая база не затрагивается).

---

## Основные маршруты

| Метод | URL | Описание |
|-------|-----|----------|
| GET/POST | `/login`, `/logout` | Авторизация |
| GET | `/employees/`, `/companies/`, `/wells/` | Списки и CRUD |
| POST | `/employees/set-role/{id}` | Назначение роли (admin) |
| GET | `/productions/` | Суточные рапорты |
| GET/POST | `/productions/create` | Создание рапорта |
| GET | `/dashboard/` | Дашборд |
| GET | `/dashboard/api/*` | JSON для графиков |
| GET | `/excel/template` | Шаблон импорта |
| POST | `/excel/import` | Импорт (фоновая задача) |
| GET | `/excel/import/status/{id}` | Статус импорта |
| GET | `/excel/export` | Запуск экспорта (фоновая задача) |
| GET | `/excel/export/status/{id}` | Статус экспорта |
| GET | `/excel/export/download/{file}` | Скачивание готового отчёта |
