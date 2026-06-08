"""
Сервис авторизации.
Содержит логику проверки credentials и работы с сессиями.
"""

import bcrypt
from sqlalchemy.orm import Session

from app.models import Employee


def authenticate_employee(db: Session, email: str, password: str) -> Employee | None:
    """
    Проверяет credentials пользователя.

    Ищет сотрудника по email и проверяет пароль через bcrypt.

    Args:
        db (Session): Сессия базы данных.
        email (str): Email из формы входа.
        password (str): Пароль из формы входа.

    Returns:
        Employee | None: Объект сотрудника если данные верны, иначе None.
    """
    employee = db.query(Employee).filter(Employee.email == email).first()
    if not employee:
        return None
    if not bcrypt.checkpw(password.encode(), employee.password.encode()):
        return None
    return employee
