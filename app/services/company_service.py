"""
Сервис для работы с нефтяными компаниями.
Содержит бизнес-логику CRUD операций.
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import OilCompany


def get_company_by_id(db: Session, company_id: int) -> OilCompany | None:
    """
    Возвращает компанию по ID.

    Args:
        db (Session): Сессия базы данных.
        company_id (int): ID компании.

    Returns:
        OilCompany | None: Объект компании или None если не найдена.
    """
    return db.query(OilCompany).filter(OilCompany.id == company_id).first()


def create_company(db: Session, name: str, region: str) -> OilCompany:
    """
    Создаёт новую нефтяную компанию.

    Args:
        db (Session): Сессия базы данных.
        name (str): Название компании.
        region (str): Регион компании.

    Returns:
        OilCompany: Созданная компания.
    """
    company = OilCompany(name=name, region=region)
    db.add(company)
    db.commit()
    return company


def update_company(
    db: Session, company_id: int, name: str, region: str
) -> OilCompany | None:
    """
    Обновляет данные компании.

    Args:
        db (Session): Сессия базы данных.
        company_id (int): ID компании.
        name (str): Новое название.
        region (str): Новый регион.

    Returns:
        OilCompany | None: Обновлённая компания или None если не найдена.
    """
    company = get_company_by_id(db, company_id)
    if not company:
        return None
    company.name = name
    company.region = region
    db.commit()
    return company


def delete_company(db: Session, company_id: int) -> bool:
    """
    Удаляет компанию.

    Не удаляет компанию, у которой есть связанные скважины или сотрудники
    (защита от нарушения внешних ключей).

    Args:
        db (Session): Сессия базы данных.
        company_id (int): ID компании.

    Returns:
        bool: True если удалена, False если не найдена или есть связи.
    """
    company = get_company_by_id(db, company_id)
    if not company:
        return False
    try:
        db.delete(company)
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False


def get_companies_paginated(
    db: Session, page: int = 1, per_page: int = 10
) -> tuple[list[OilCompany], int]:
    """
    Возвращает компании с пагинацией.

    Args:
        db (Session): Сессия базы данных.
        page (int): Номер страницы.
        per_page (int): Количество записей на странице.

    Returns:
        tuple: (список компаний, общее количество).
    """
    total = db.query(OilCompany).count()
    companies = (
        db.query(OilCompany)
        .order_by(OilCompany.name)
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return companies, total
