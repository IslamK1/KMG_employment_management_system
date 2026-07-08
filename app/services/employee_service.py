"""
Сервис для работы с сотрудниками.
Содержит всю бизнес-логику CRUD операций.
"""

import bcrypt
from sqlalchemy.orm import Session

from app.models import Employee, OilCompany


def get_all_employees(db: Session) -> list[type[Employee]]:
    """
    Возвращает список всех сотрудников из БД.

    Args:
        db (Session): Сессия базы данных.

    Returns:
        list[Employee]: Список всех сотрудников.
    """
    return db.query(Employee).all()


def get_employee_by_id(db: Session, emp_id: int) -> type[Employee] | None:
    """
    Возвращает сотрудника по ID.

    Args:
        db (Session): Сессия базы данных.
        emp_id (int): ID сотрудника.

    Returns:
        Employee | None: Объект сотрудника или None если не найден.
    """
    return db.query(Employee).filter(Employee.id == emp_id).first()


def get_employee_by_email(db: Session, email: str) -> type[Employee] | None:
    """
    Возвращает сотрудника по email.

    Args:
        db (Session): Сессия базы данных.
        email (str): Email сотрудника.

    Returns:
        Employee | None: Объект сотрудника или None если не найден.
    """
    return db.query(Employee).filter(Employee.email == email).first()


def get_all_companies(db: Session) -> list[type[OilCompany]]:
    """
    Возвращает список всех нефтяных компаний.

    Args:
        db (Session): Сессия базы данных.

    Returns:
        list[OilCompany]: Список всех компаний.
    """
    return db.query(OilCompany).all()


def create_employee(
    db: Session,
    name: str,
    email: str,
    position: str,
    password: str,
    oil_company_id: int | None,
) -> Employee | None:
    """
    Создаёт нового сотрудника в БД.

    Проверяет уникальность email перед созданием.
    Хэширует пароль через bcrypt перед сохранением.

    Args:
        db (Session): Сессия базы данных.
        name (str): Имя сотрудника.
        email (str): Email сотрудника.
        position (str): Должность сотрудника.
        password (str): Пароль в открытом виде.
        oil_company_id (int | None): ID компании.

    Returns:
        Employee | None: Созданный сотрудник или None если email занят.
    """
    existing = get_employee_by_email(db, email)
    if existing:
        return None

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    emp = Employee(
        name=name,
        email=email,
        position=position,
        password=hashed_password,
        oil_company_id=oil_company_id,
    )
    db.add(emp)
    db.commit()
    return emp


def update_employee(
    db: Session,
    emp_id: int,
    name: str,
    email: str,
    position: str,
    oil_company_id: int | None,
) -> Employee | None:
    """
    Обновляет данные сотрудника в БД.

    Args:
        db (Session): Сессия базы данных.
        emp_id (int): ID сотрудника.
        name (str): Новое имя.
        email (str): Новый email.
        position (str): Новая должность.
        oil_company_id (int | None): Новый ID компании.

    Returns:
        Employee | None: Обновлённый сотрудник или None если не найден.
    """
    emp = get_employee_by_id(db, emp_id)
    if not emp:
        return None

    emp.name = name
    emp.email = email
    emp.position = position
    emp.oil_company_id = oil_company_id
    db.commit()
    return emp


def delete_employee(db: Session, emp_id: int) -> bool:
    """
    Удаляет сотрудника из БД.

    Args:
        db (Session): Сессия базы данных.
        emp_id (int): ID сотрудника.

    Returns:
        bool: True если удалён, False если не найден.
    """
    emp = get_employee_by_id(db, emp_id)
    if not emp:
        return False

    db.delete(emp)
    db.commit()
    return True


def get_employees_paginated(
    db: Session, page: int = 1, per_page: int = 10
) -> tuple[list[type[Employee]], int]:
    """
    Возвращает сотрудников с пагинацией.

    Args:
        db (Session): Сессия базы данных.
        page (int): Номер страницы.
        per_page (int): Количество записей на странице.

    Returns:
        tuple: (список сотрудников, общее количество).
    """
    total = db.query(Employee).count()
    employees = db.query(Employee).offset((page - 1) * per_page).limit(per_page).all()
    return employees, total


def set_employee_role(db: Session, emp_id: int, role: str) -> bool:
    """
    Меняет роль сотрудника (используется админом при назначении менеджеров).

    Args:
        db (Session): Сессия базы данных.
        emp_id (int): Идентификатор сотрудника.
        role (str): Новая роль — admin, manager или operator.

    Returns:
        bool: True если роль изменена, False если сотрудник не найден
              или роль недопустима.
    """
    if role not in ("admin", "manager", "operator"):
        return False
    employee = db.query(Employee).filter(Employee.id == emp_id).first()
    if not employee:
        return False
    employee.role = role
    db.commit()
    return True
