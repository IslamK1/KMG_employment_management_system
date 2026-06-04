# Employee Management System

Веб-приложение для управления сотрудниками нефтяных компаний.

---

## Стек технологий

- **FastAPI** - веб фреймворк
- **SQLAlchemy** — ORM для работы с базой данных
- **Alembic** — миграции базы данных
- **PostgreSQL** — база данных
- **Jinja2** — HTML шаблоны
- **bcrypt** — хэширование паролей
- **Faker** — генерация тестовых данных
- **Ruff** — линтер и форматтер кода (PEP-8)
- **Starlette Sessions** — сессионная авторизация

---

## Функционал

- Авторизация через сессии (вход / выход)
- Защита маршрутов — неавторизованный пользователь редиректится на /login
- CRUD сотрудников — создание, просмотр, редактирование, удаление
- Привязка сотрудников и скважин к нефтяным компаниям
- Автоматическая генерация тестовых данных через Faker
- Суточные производственные показатели скважин за 365 дней
- Bulk Insert для быстрой вставки больших объёмов данных

---

## Структура проекта

    employee-management-system/
    │
    ├── app/
    │   ├── routers/
    │   │   ├── __init__.py
    │   │   ├── auth.py              # Роуты авторизации (login/logout)
    │   │   └── employees.py         # CRUD роуты сотрудников
    │   │
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── employee.py          # Модель сотрудника
    │   │   ├── oil_company.py       # Модель нефтяной компании
    │   │   ├── well.py              # Модель скважины
    │   │   └── daily_production.py  # Модель суточных показателей
    │   │
    │   ├── __init__.py
    │   ├── main.py                  # Точка входа приложения
    │   ├── database.py              # Подключение к БД, сессии
    │   └── dependencies.py          # Проверка авторизации
    │
    ├── seeders/
    │   ├── seed.py                  # Создание admin пользователя
    │   └── seed_data.py             # Генерация тестовых данных
    │
    ├── providers/
    │   ├── __init__.py
    │   └── oil_provider.py          # Кастомный Faker провайдер
    │
    ├── migrations/                  # Alembic миграции
    │   └── versions/
    │
    ├── templates/
    │   ├── login.html
    │   └── employees/
    │       ├── index.html
    │       ├── create.html
    │       ├── edit.html
    │       └── show.html
    │
    ├── static/
    │   └── style.css
    │
    ├── Makefile                     # Команды для запуска проекта
    ├── ruff.toml                    # Конфиг линтера
    ├── alembic.ini                  # Конфиг миграций
    ├── requirements.txt
    ├── .env                         # Переменные окружения (не в git)
    ├── .gitignore
    └── README.md

---

## Требования

- Python 3.10+
- PostgreSQL

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
source venv/Scripts/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Создать .env файл и положить туда ссылку на базу данных

```Создайте файл .env в корне проекта с данным содержимым внутри:
DATABASE_URL=postgresql://postgres:ТВОй_ПАРОЛЬ@localhost:5432/employee_management
```

### 5. Создать базу данных в PostgreSQL

```sql
CREATE DATABASE employee_management;
```

### 6. Применить миграции

```bash
make migrate
```

### 7. Создать admin пользователя

```bash
make seed
```

### 8. Заполнить базу тестовыми данными (опционально)

```bash
make data
```

### 9. Запустить сервер

```bash
make run 
```

Открыть в браузере: **http://127.0.0.1:8000**

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
