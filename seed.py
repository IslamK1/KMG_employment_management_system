import bcrypt

from app.database import SessionLocal, engine, Base
from app.models import Employee

# Создаём таблицы если их нет (на случай если запускаем до старта сервера)
Base.metadata.create_all(bind=engine)

# Открываем сессию для работы с БД
db = SessionLocal()

# Проверяем — вдруг такой пользователь уже есть
# Защита от дублирования при повторном запуске скрипта
existing = db.query(Employee).filter(Employee.email == "admin@mail.ru").first()

if not existing:
    # Хэшируем пароль — нельзя хранить пароль в открытом виде
    # gensalt() — случайная соль, делает хэш уникальным каждый раз
    # .encode() — строка → байты (bcrypt работает только с байтами)
    # .decode() — байты → строка для хранения в БД
    hashed = bcrypt.hashpw("12345".encode(), bcrypt.gensalt()).decode()

    # Создаём первого администратора
    user = Employee(
        name="Admin",
        email="admin@mail.ru",
        position="Administrator",
        password=hashed
    )

    db.add(user)    # добавляем в сессию
    db.commit()     # сохраняем в БД
    print("Пользователь создан: admin@mail.ru / 12345")
else:
    print("Пользователь уже существует")

# Закрываем соединение с БД
db.close()