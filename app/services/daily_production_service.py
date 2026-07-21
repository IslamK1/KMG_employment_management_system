"""
Сервис для работы с суточными производственными показателями.
Содержит бизнес-логику CRUD операций и защиту от двойного ввода.
"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app import cache
from app.models import DailyProduction, Well
from app.schemas import DailyProductionCreate

# Eager loading: подгружаем скважину и её компанию заранее, одним набором
# запросов. Без этого шаблон дёргает БД на каждую строку рапорта — классический N+1.
_EAGER = selectinload(DailyProduction.well).selectinload(Well.oil_company)


def get_all_reports(db: Session) -> list[type[DailyProduction]]:
    """
    Возвращает все суточные рапорты отсортированные по дате.

    Args:
        db (Session): Сессия базы данных.

    Returns:
        list[DailyProduction]: Список всех рапортов.
    """
    return (
        db.query(DailyProduction)
        .options(_EAGER)
        .order_by(DailyProduction.date.desc())
        .all()
    )


def get_report_by_id(db: Session, report_id: int) -> type[DailyProduction] | None:
    """
    Возвращает рапорт по ID.

    Args:
        db (Session): Сессия базы данных.
        report_id (int): ID рапорта.

    Returns:
        DailyProduction | None: Объект рапорта или None если не найден.
    """
    return db.query(DailyProduction).filter(DailyProduction.id == report_id).first()


def check_duplicate(db: Session, well_id: int, report_date: date) -> bool:
    """
    Проверяет существует ли рапорт для данной скважины на данную дату.

    Args:
        db (Session): Сессия базы данных.
        well_id (int): ID скважины.
        report_date (date): Дата рапорта.

    Returns:
        bool: True если рапорт уже существует, False если нет.
    """
    existing = (
        db.query(DailyProduction)
        .filter(
            DailyProduction.well_id == well_id,
            DailyProduction.date == report_date,
        )
        .first()
    )
    return existing is not None


def create_report(
    db: Session, data: DailyProductionCreate
) -> tuple[DailyProduction | None, str | None]:
    """
    Создаёт новый суточный рапорт.

    Защищает от двойного ввода рапорта по одной скважине в один день.

    Args:
        db (Session): Сессия базы данных.
        data (DailyProductionCreate): Валидированные данные рапорта.

    Returns:
        tuple: (DailyProduction, None) при успехе или (None, сообщение_об_ошибке).
    """
    if check_duplicate(db, data.well_id, data.date):
        return None, "Рапорт для этой скважины на данную дату уже существует"

    report = DailyProduction(
        well_id=data.well_id,
        date=data.date,
        working_hours=data.working_hours,
        liquid_volume=data.liquid_volume,
        water_cut=data.water_cut,
        density=data.density,
    )

    try:
        db.add(report)
        db.commit()
        cache.invalidate()  # данные изменились — сбрасываем кэш дашборда
        return report, None
    except IntegrityError:
        db.rollback()
        return None, "Рапорт для этой скважины на данную дату уже существует"


def delete_report(db: Session, report_id: int) -> bool:
    """
    Удаляет суточный рапорт.

    Args:
        db (Session): Сессия базы данных.
        report_id (int): ID рапорта.

    Returns:
        bool: True если удалён, False если не найден.
    """
    report = get_report_by_id(db, report_id)
    if not report:
        return False
    db.delete(report)
    db.commit()
    cache.invalidate()  # данные изменились — сбрасываем кэш дашборда
    return True


def get_all_wells(db: Session) -> list[type[Well]]:
    """
    Возвращает список всех скважин для формы выбора.

    Args:
        db (Session): Сессия базы данных.

    Returns:
        list[Well]: Список всех скважин.
    """
    return db.query(Well).all()


def get_wells_for_company(db: Session, company_id: int) -> list[type[Well]]:
    """
    Возвращает скважины конкретной компании.

    Нужно для оператора: он выбирает скважину только из своей компании.

    Args:
        db (Session): Сессия базы данных.
        company_id (int): Идентификатор компании.

    Returns:
        list[Well]: Скважины этой компании.
    """
    return db.query(Well).filter(Well.oil_company_id == company_id).all()


def well_belongs_to_company(db: Session, well_id: int, company_id: int) -> bool:
    """
    Проверяет, что скважина принадлежит указанной компании.

    Защита от подмены well_id в форме: оператор не сможет создать
    рапорт по чужой скважине, даже если подставит её id вручную.

    Args:
        db (Session): Сессия базы данных.
        well_id (int): Идентификатор скважины.
        company_id (int): Идентификатор компании.

    Returns:
        bool: True если скважина принадлежит компании.
    """
    well = db.query(Well).filter(Well.id == well_id).first()
    return well is not None and well.oil_company_id == company_id


def is_report_locked(report_date, edit_days: int = 7) -> bool:
    """
    Проверяет, старше ли рапорт разрешённого срока редактирования.

    Рапорты старше edit_days дней нельзя редактировать/удалять
    (кроме админа — эта проверка вызывается только для не-админов).

    Args:
        report_date: Дата рапорта.
        edit_days (int): Сколько дней рапорт доступен для правки.

    Returns:
        bool: True если рапорт «заморожен» (старше срока).
    """
    from datetime import date, timedelta

    return report_date < date.today() - timedelta(days=edit_days)


def get_reports_paginated(
    db: Session, page: int = 1, per_page: int = 10, company_id: int | None = None
) -> tuple[list[type[DailyProduction]], int]:
    """
    Возвращает рапорты с пагинацией.

    Args:
        db (Session): Сессия базы данных.
        page (int): Номер страницы.
        per_page (int): Количество записей на странице.
        company_id (int | None): Если задан — только рапорты по скважинам
            этой компании (manager и operator видят лишь свою компанию).

    Returns:
        tuple: (список рапортов, общее количество).
    """
    base = db.query(DailyProduction).options(_EAGER)
    if company_id is not None:
        own_wells = select(Well.id).where(Well.oil_company_id == company_id)
        base = base.filter(DailyProduction.well_id.in_(own_wells))

    total = base.count()
    reports = (
        base.order_by(DailyProduction.date.desc(), DailyProduction.id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return reports, total
