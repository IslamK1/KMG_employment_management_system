# Employee Management System

Веб-приложение для управления сотрудниками компании с системой авторизации и полным CRUD функционалом.

---

##  Стек технологий

- **FastAPI** — веб-фреймворк
- **SQLAlchemy** — ORM для работы с базой данных
- **Jinja2** — HTML шаблоны
- **SQLite** — база данных
- **bcrypt** — хэширование паролей
- **Starlette Sessions** — сессионная авторизация

---

##  Функционал

-  Авторизация через сессии (вход / выход)
-  Защита маршрутов — неавторизованный пользователь редиректится на /login
-  CRUD сотрудников — создание, просмотр, редактирование, удаление
-  HTML страницы на Jinja2 шаблонах

---

##  Структура проекта

employee-management-system/
│
├── app/
│   ├── main.py              # Точка входа, подключение роутеров и middleware
│   ├── database.py          # Подключение к БД, сессии
│   ├── models.py            # Модель Employee (таблица в БД)
│   ├── auth.py              # Роуты авторизации (login/logout)
│   ├── employee_routes.py   # CRUD роуты сотрудников
│   └── dependencies.py      # Проверка авторизации
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
├── seed.py                  # Создание первого пользователя
├── requirements.txt
├── .gitignore
└── README.md

---

##  Запуск проекта

### 1. Клонировать репозиторий
```bash
git clone https://github.com/ТВО_ИМЯ/employee-management-system.git
cd employee-management-system
```

### 2. Создать виртуальную среду
```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Установить зависимости
```bash
pip install -r requirements.txt
```

### 4. Создать первого пользователя
```bash
python seed.py
```

### 5. Запустить сервер
```bash
uvicorn app.main:app --reload
```

Открыть в браузере: **http://127.0.0.1:8000**

---

##  Данные для входа (после seed.py)
Email:    admin@mail.ru
Пароль:   12345

---

##  Маршруты

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