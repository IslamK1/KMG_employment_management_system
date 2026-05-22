from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.database import Base, engine
from app.auth import router as auth_router
from app.employee_routes import router as emp_router

# При старте приложения создаём все таблицы в БД если их нет
# Смотрит на все классы которые наследуют Base (Employee и тд)
# Если таблица уже существует — не трогает её
Base.metadata.create_all(bind=engine)

# Создаём главное приложение FastAPI
app = FastAPI(title="Employee Management System")

# Подключаем middleware сессий
# Middleware — код который выполняется при КАЖДОМ запросе до роута
# SessionMiddleware добавляет request.session — зашифрованный словарь в cookie
# secret_key — ключ шифрования, без него нельзя прочитать/подделать сессию
app.add_middleware(
    SessionMiddleware,
    secret_key="a3f8e2c1b9d4f7a6e5c2b8d1f4a7e3c6b9d2f5a8e1c4b7d0f3a6e9c2b5d8f1"
)

# Подключаем статические файлы (CSS, JS, картинки)
# Теперь файл static/style.css доступен по URL /static/style.css
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем роутеры из отдельных файлов
# auth_router добавляет роуты: /login, /logout
# emp_router добавляет роуты: /employees/, /employees/create, и тд
app.include_router(auth_router)
app.include_router(emp_router)


# Корневой маршрут — редиректим с / на /employees/
# Чтобы при открытии сайта сразу попадать на дашборд (или на логин)
@app.get("/")
def root():
    return RedirectResponse(url="/employees/")