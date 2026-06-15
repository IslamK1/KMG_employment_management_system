# Employee Management System

Веб-приложение для управления сотрудниками нефтяных компаний с дашбордом мониторинга добычи.

---

## Стек технологий

- **FastAPI** — веб-фреймворк
- **SQLAlchemy** — ORM для работы с базой данных
- **Alembic** — миграции базы данных
- **PostgreSQL** — база данных
- **Jinja2** — HTML-шаблоны
- **bcrypt** — хэширование паролей
- **Faker** — генерация тестовых данных
- **Ruff** — линтер и форматтер кода (PEP-8)
- **Starlette Sessions** — сессионная авторизация
- **TailwindCSS** — утилитарный CSS-фреймворк (через Tailwind CLI)
- **Chart.js** — визуализация данных на дашборде

---

## Функционал

- Авторизация через сессии (вход / выход)
- Защита маршрутов — неавторизованный пользователь редиректится на `/login`
- CRUD сотрудников — создание, просмотр, редактирование, удаление
- Привязка сотрудников и скважин к нефтяным компаниям
- Автоматическая генерация тестовых данных через Faker
- Суточные производственные рапорты скважин:
  - валидация на уровне схемы и БД (время работы 0–24 ч, обводненность 0–100%)
  - уникальное ограничение `UniqueConstraint(well + date)` — один рапорт на скважину в день
  - расчёт чистой нефти через `@property` по формуле `Жидкость * (1 - Вода/100) * Плотность`
- Bulk Insert для быстрой вставки больших объёмов данных
- Корпоративный интерфейс на TailwindCSS — боковая и верхняя навигация, формы и таблицы
- Дашборд руководства с 4 графиками и фильтром по диапазону дат:
  - динамика добычи чистой нефти
  - обводненность скважин одной компании
  - распределение фонда скважин по типам
  - топ компаний по добыче
  - KPI-карточки (суммарная нефть, средняя обводненность, число скважин и компаний)

---

## Структура проекта

    employee-management-system/
    │
    ├── app/
    │   ├── routers/
    │   │   ├── __init__.py
    │   │   ├── auth.py                 # Роуты авторизации (login/logout)
    │   │   ├── employees.py            # CRUD роуты сотрудников
    │   │   ├── daily_productions.py    # Роуты суточных рапортов
    │   │   └── dashboard.py            # Страница дашборда + JSON API для графиков
    │   │
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── employee.py             # Модель сотрудника
    │   │   ├── oil_company.py          # Модель нефтяной компании
    │   │   ├── well.py                 # Модель скважины
    │   │   └── daily_production.py     # Модель суточных показателей
    │   │
    │   ├── schemas/
    │   │   ├── __init__.py
    │   │   └── daily_production.py     # Pydantic-схема с валидацией рапорта
    │   │
    │   ├── services/
    │   │   ├── __init__.py
    │   │   ├── auth_service.py         # Логика авторизации
    │   │   ├── employee_service.py     # Логика сотрудников
    │   │   ├── daily_production_service.py  # Логика рапортов
    │   │   └── dashboard_service.py    # Агрегация данных для графиков
    │   │
    │   ├── __init__.py
    │   ├── main.py                     # Точка входа приложения
    │   ├── database.py                 # Подключение к БД, сессии
    │   └── dependencies.py             # Проверка авторизации
    │
    ├── seeders/
    │   ├── seed.py                     # Создание admin пользователя
    │   └── seed_data.py                # Генерация тестовых данных
    │
    ├── providers/
    │   ├── __init__.py
    │   └── oil_provider.py             # Кастомный Faker провайдер
    │
    ├── migrations/                     # Alembic миграции
    │   └── versions/
    │
    ├── templates/
    │   ├── base.html                   # Базовый шаблон (sidebar + topbar)
    │   ├── login.html
    │   ├── partials/
    │   │   ├── sidebar.html            # Боковая навигация
    │   │   ├── topbar.html             # Верхняя навигация
    │   │   └── pagination.html         # Пагинация
    │   ├── employees/
    │   │   ├── index.html
    │   │   ├── create.html
    │   │   ├── edit.html
    │   │   └── show.html
    │   ├── productions/
    │   │   ├── index.html
    │   │   ├── create.html
    │   │   └── show.html
    │   └── dashboard/
    │       └── index.html              # Дашборд с графиками
    │
    ├── static/
    │   ├── src/
    │   │   └── input.css               # Исходник Tailwind (@import)
    │   ├── style.css                   # Скомпилированный CSS (генерируется)
    │   └── js/
    │       └── chart.umd.js            # Chart.js (копируется из node_modules)
    │
    ├── Makefile                        # Команды для запуска проекта
    ├── ruff.toml                       # Конфиг линтера
    ├── alembic.ini                     # Конфиг миграций
    ├── package.json                    # npm-зависимости (Tailwind, Chart.js)
    ├── requirements.txt
    ├── .env                            # Переменные окружения (не в git)
    ├── .gitignore
    └── README.md

---

## Требования

- Python 3.10+
- PostgreSQL
- Node.js 18+ (для сборки TailwindCSS и Chart.js)

---

## Запуск проекта

### 1. Клонировать репозиторий

```bash
git clone https://github.com/IslamK1/KMG_employment_management_system.git
cd employee-management-system
```

### 2. Создать виртуальную среду

```bash
python -m venv .venv
```

Mac/Linux:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

### 3. Установить Python-зависимости

```bash
pip install -r requirements.txt
```

### 4. Установить frontend-зависимости

```bash
npm install
```

### 5. Создать .env файл с ссылкой на базу данных

Создайте файл `.env` в корне проекта со следующим содержимым:

```
DATABASE_URL=postgresql://postgres:ТВОЙ_ПАРОЛЬ@localhost:5432/employee_management
```

### 6. Создать базу данных в PostgreSQL

```sql
CREATE DATABASE employee_management;
```

### 7. Применить миграции

```bash
make migrate
```

### 8. Создать admin пользователя

```bash
make seed
```

### 9. Заполнить базу тестовыми данными (опционально)

```bash
make data
```

### 10. Собрать стили и скрипты

```bash
make css
make js
```

### 11. Запустить сервер

```bash
make run
```

Открыть в браузере: **http://127.0.0.1:8000**

---

## Разработка фронтенда

При работе над шаблонами удобно держать пересборку CSS в отдельном терминале — он будет следить за изменениями и пересобирать `style.css` автоматически:

```bash
make css-watch
```

---

## Данные для входа

    Email:    admin@mail.ru
    Пароль:   12345

---

## Команды Makefile

| Команда | Описание |
|---------|----------|
| `make run` | Запустить сервер |
| `make migrate` | Применить миграции |
| `make seed` | Создать admin пользователя |
| `make data` | Заполнить БД тестовыми данными |
| `make format` | Форматировать код через Ruff |
| `make format-check` | Проверить код без изменений |
| `make css` | Собрать TailwindCSS в `static/style.css` |
| `make css-watch` | Пересобирать CSS при изменении шаблонов |
| `make js` | Скопировать Chart.js в `static/js/` |

---

## Маршруты

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/login` | Страница входа |
| POST | `/login` | Обработка формы входа |
| GET | `/logout` | Выход из системы |
| GET | `/employees/` | Список сотрудников |
| GET | `/employees/create` | Форма создания |
| POST | `/employees/create` | Создание сотрудника |
| GET | `/employees/{id}` | Просмотр сотрудника |
| GET | `/employees/edit/{id}` | Форма редактирования |
| POST | `/employees/edit/{id}` | Обновление сотрудника |
| GET | `/employees/delete/{id}` | Удаление сотрудника |
| GET | `/productions/` | Список суточных рапортов |
| GET | `/productions/create` | Форма создания рапорта |
| POST | `/productions/create` | Создание рапорта |
| GET | `/productions/{id}` | Просмотр рапорта |
| GET | `/productions/delete/{id}` | Удаление рапорта |
| GET | `/dashboard/` | Дашборд с графиками |
| GET | `/dashboard/api/kpis` | JSON: ключевые показатели |
| GET | `/dashboard/api/oil-dynamics` | JSON: динамика добычи нефти |
| GET | `/dashboard/api/water-cut` | JSON: обводненность скважин |
| GET | `/dashboard/api/well-types` | JSON: распределение фонда скважин |
| GET | `/dashboard/api/top-companies` | JSON: топ компаний по добыче |

JSON-эндпоинты дашборда принимают необязательные query-параметры `date_from` и `date_to` (формат `YYYY-MM-DD`) для фильтрации по диапазону дат.