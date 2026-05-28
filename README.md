# Employee Management System

Веб-приложение для управления сотрудниками нефтяных компаний.

---

## Стек технологий

- **FastAPI**еб-фреймворк
- **SQLAlchemy** — ORM для работы с базой данных
- **Alembic** — миграции базы данных
- **PostgreSQL** — база данных
- **Jinja2** — HTML шаблоны
- **bcrypt** — хэширование паролей
- **Faker** — генерация тестовых данных
- **Starlette Sessions** — сессионная авторизация

---

## Функционал

- Авторизация через сессии (вход / выход)
- Защита маршрутов — неавторизованный пользователь редиректится на /login
- CRUD сотрудников — создание, просмотр, редактирование, удаление
- Привязка сотрудников и скважин к нефтяным компаниям
- Автоматическая генерация тестовых данных через Faker
- Суточные производственные показатели скважин за 365 дней

---

## Структура проекта

    employee-management-system/
    │
    ├── app/
    │   ├── main.py              # Точка входа, подключение роутеров и middleware
    │   ├── database.py          # Подключение к БД, сессии
    │   ├── auth.py              # Роуты авторизации (login/logout)
    │   ├── employee_routes.py   # CRUD роуты сотрудников
    │   ├── dependencies.py      # Проверка авторизации
    │   └── models/
    │       ├── __init__.py
    │       ├── employee.py      # Модель сотрудника
    │       ├── oil_company.py   # Модель нефтяной компании
    │       ├── well.py          # Модель скважины
    │       └── daily_production.py  # Модель суточных показателей
    │
    ├── migrations/              # Alembic миграции
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
    ├── seed.py                  # Создание admin пользователя
    ├── seed_data.py             # Генерация тестовых данных
    ├── requirements.txt
    ├── .env                     # Переменные окружения (не в git)
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
python -m venv venv
```

Mac/Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Создать .env файл

Создайте файл '.env' в корне проекта: 

DATABASE_URL=postgresql://postgres:ТВОй_ПАРОЛЬ@localhost:5432/employee_management

### 5. Создать базу данных в PostgreSQL

```sql
CREATE DATABASE employee_management;
```

### 6. Применить миграции

```bash
alembic upgrade head
```

### 7. Создать admin пользователя

```bash
python seed.py
```

### 8. Заполнить базу тестовыми данными (опционально)

```bash
python seed_data.py
```

### 9. Запустить сервер

```bash
uvicorn app.main:app --reload
```

Открыть в браузере: **http://127.0.0.1:8000**

---

## Данные для входа

Email:    admin@mail.ru
Пароль:   12345

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