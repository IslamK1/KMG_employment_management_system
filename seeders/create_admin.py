"""
Создание учётной записи администратора при старте контейнера.

Аналог `createsuperuser` в Django. Скрипт идемпотентный: если админ
уже есть — ничего не делает, поэтому его безопасно вызывать при каждом
запуске Docker. Логин и пароль берутся из переменных окружения
(с безопасными значениями по умолчанию).
"""

import os

import bcrypt

from app.database import Base, SessionLocal, engine
from app.models import Employee

# на случай первого запуска — гарантируем, что таблицы существуют
Base.metadata.create_all(bind=engine)

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@mail.ru")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "12345")
ADMIN_NAME = os.getenv("ADMIN_NAME", "Admin")


def _hash(password: str) -> str:
    """Хэширует пароль через bcrypt (как при обычной регистрации)."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def main() -> None:
    db = SessionLocal()
    try:
        existing = db.query(Employee).filter(Employee.email == ADMIN_EMAIL).first()
        if existing:
            print(f"Администратор {ADMIN_EMAIL} уже существует — пропускаем.")
            return

        db.add(
            Employee(
                name=ADMIN_NAME,
                email=ADMIN_EMAIL,
                position="Administrator",
                password=_hash(ADMIN_PASSWORD),
                role="admin",
                oil_company_id=None,
            )
        )
        db.commit()
        print(f"Создан администратор: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
