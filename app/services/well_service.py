"""
Сервис для работы со скважинами.
Содержит бизнес-логику CRUD операций.
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Well


def get_well_by_id(db: Session, well_id: int) -> Well | None:
    """
    Возвращает скважину по ID.

    Args:
        db (Session): Сессия базы данных.
        well_id (int): ID скважины.

    Returns:
        Well | None: Объект скважины или None если не найдена.
    """
    return db.query(Well).filter(Well.id == well_id).first()


def create_well(
    db: Session,
    name: str,
    type: str,
    max_drilling_depth: int,
    oil_company_id: int,
) -> Well:
    """
    Создаёт новую скважину.

    Args:
        db (Session): Сессия базы данных.
        name (str): Название скважины.
        type (str): Тип скважины.
        max_drilling_depth (int): Максимальная глубина бурения в метрах.
        oil_company_id (int): ID компании-владельца.

    Returns:
        Well: Созданная скважина.
    """
    well = Well(
        name=name,
        type=type,
        max_drilling_depth=max_drilling_depth,
        oil_company_id=oil_company_id,
    )
    db.add(well)
    db.commit()
    return well


def update_well(
    db: Session,
    well_id: int,
    name: str,
    type: str,
    max_drilling_depth: int,
    oil_company_id: int,
) -> Well | None:
    """
    Обновляет данные скважины.

    Args:
        db (Session): Сессия базы данных.
        well_id (int): ID скважины.
        name (str): Новое название.
        type (str): Новый тип.
        max_drilling_depth (int): Новая глубина бурения.
        oil_company_id (int): Новый ID компании.

    Returns:
        Well | None: Обновлённая скважина или None если не найдена.
    """
    well = get_well_by_id(db, well_id)
    if not well:
        return None
    well.name = name
    well.type = type
    well.max_drilling_depth = max_drilling_depth
    well.oil_company_id = oil_company_id
    db.commit()
    return well


def delete_well(db: Session, well_id: int) -> bool:
    """
    Удаляет скважину.

    Не удаляет скважину, у которой есть суточные рапорты
    (защита от нарушения внешних ключей).

    Args:
        db (Session): Сессия базы данных.
        well_id (int): ID скважины.

    Returns:
        bool: True если удалена, False если не найдена или есть рапорты.
    """
    well = get_well_by_id(db, well_id)
    if not well:
        return False
    try:
        db.delete(well)
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False


def get_wells_paginated(
    db: Session, page: int = 1, per_page: int = 10, company_id: int | None = None
) -> tuple[list[Well], int]:
    """
    Возвращает скважины с пагинацией.

    Args:
        db (Session): Сессия базы данных.
        page (int): Номер страницы.
        per_page (int): Количество записей на странице.
        company_id (int | None): Если задан — только скважины этой компании
            (для менеджера, который видит лишь свою компанию).

    Returns:
        tuple: (список скважин, общее количество).
    """
    base = db.query(Well)
    if company_id is not None:
        base = base.filter(Well.oil_company_id == company_id)

    total = base.count()
    wells = base.order_by(Well.name).offset((page - 1) * per_page).limit(per_page).all()
    return wells, total
