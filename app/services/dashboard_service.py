"""
Сервис агрегации данных для дашборда руководства.

Считает бизнес-показатели добычи в разрезе компаний и скважин
для построения графиков на главной странице мониторинга.
Поддерживает фильтрацию по диапазону дат и по компании (для менеджера,
который видит показатели только своей компании).
"""

from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import DailyProduction, OilCompany, Well

# Формула чистой нефти на уровне SQL: Жидкость * (1 - Вода/100) * Плотность
OIL_EXPR = (
    DailyProduction.liquid_volume
    * (1 - DailyProduction.water_cut / 100)
    * DailyProduction.density
)


def _apply_date_filter(query, date_from: date | None, date_to: date | None):
    """Применяет фильтр по диапазону дат к запросу, если даты переданы."""
    if date_from:
        query = query.filter(DailyProduction.date >= date_from)
    if date_to:
        query = query.filter(DailyProduction.date <= date_to)
    return query


def _apply_company_filter(query, company_id: int | None):
    """
    Ограничивает запрос скважинами одной компании.

    Работает для запросов по DailyProduction: фильтрует по well_id,
    принадлежащим компании. Если company_id None (admin) — без фильтра.
    """
    if company_id is None:
        return query
    from sqlalchemy import select

    subquery = select(Well.id).where(Well.oil_company_id == company_id)
    return query.filter(DailyProduction.well_id.in_(subquery))


def get_oil_dynamics(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    company_id: int | None = None,
) -> dict:
    """
    Динамика суммарной добычи чистой нефти по датам.

    Returns:
        dict: {"labels": [даты], "values": [тонны]}
    """
    query = db.query(DailyProduction.date, func.sum(OIL_EXPR))
    query = _apply_date_filter(query, date_from, date_to)
    query = _apply_company_filter(query, company_id)
    rows = query.group_by(DailyProduction.date).order_by(DailyProduction.date).all()
    return {
        "labels": [str(r[0]) for r in rows],
        "values": [round(r[1] or 0, 2) for r in rows],
    }


def get_water_cut_by_company(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    company_id: int | None = None,
) -> dict:
    """
    Средняя обводненность скважин одной компании.

    Если company_id не передан — берётся компания с наибольшим числом скважин
    (для admin, который смотрит весь холдинг). Для менеджера всегда его компания.

    Returns:
        dict: {"company": название, "labels": [скважины], "values": [%]}
    """
    if company_id is None:
        first = (
            db.query(Well.oil_company_id, func.count(Well.id))
            .join(DailyProduction, DailyProduction.well_id == Well.id)
            .group_by(Well.oil_company_id)
            .order_by(func.count(Well.id).desc())
            .first()
        )
        company_id = first[0] if first else None

    company = db.query(OilCompany).filter(OilCompany.id == company_id).first()

    query = (
        db.query(Well.name, func.avg(DailyProduction.water_cut))
        .join(DailyProduction, DailyProduction.well_id == Well.id)
        .filter(Well.oil_company_id == company_id)
    )
    query = _apply_date_filter(query, date_from, date_to)
    rows = query.group_by(Well.name).order_by(Well.name).all()

    return {
        "company": company.name if company else "—",
        "labels": [r[0] for r in rows],
        "values": [round(r[1] or 0, 1) for r in rows],
    }


def get_well_types_distribution(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    company_id: int | None = None,
) -> dict:
    """
    Распределение фонда скважин по типам.

    Считает только скважины у которых есть рапорты в выбранном периоде.

    Returns:
        dict: {"labels": [типы], "values": [количество]}
    """
    query = db.query(Well.type, func.count(func.distinct(Well.id))).join(
        DailyProduction, DailyProduction.well_id == Well.id
    )
    query = _apply_date_filter(query, date_from, date_to)
    if company_id is not None:
        query = query.filter(Well.oil_company_id == company_id)
    rows = (
        query.group_by(Well.type)
        .order_by(func.count(func.distinct(Well.id)).desc())
        .all()
    )

    return {
        "labels": [r[0] for r in rows],
        "values": [r[1] for r in rows],
    }


def get_top_companies(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = 10,
    company_id: int | None = None,
) -> dict:
    """
    Топ компаний по суммарной добыче чистой нефти.

    Для менеджера (company_id задан) вернётся одна его компания.

    Returns:
        dict: {"labels": [компании], "values": [тонны]}
    """
    query = (
        db.query(OilCompany.name, func.sum(OIL_EXPR))
        .join(Well, Well.oil_company_id == OilCompany.id)
        .join(DailyProduction, DailyProduction.well_id == Well.id)
    )
    query = _apply_date_filter(query, date_from, date_to)
    if company_id is not None:
        query = query.filter(OilCompany.id == company_id)
    rows = (
        query.group_by(OilCompany.name)
        .order_by(func.sum(OIL_EXPR).desc())
        .limit(limit)
        .all()
    )

    return {
        "labels": [r[0] for r in rows],
        "values": [round(r[1] or 0, 2) for r in rows],
    }


def get_kpis(
    db: Session,
    date_from: date | None = None,
    date_to: date | None = None,
    company_id: int | None = None,
) -> dict:
    """
    Ключевые показатели для карточек дашборда.

    Returns:
        dict: суммарная нефть, число скважин, число компаний, средняя обводненность.
    """
    # Суммарная добыча нефти за период
    oil_q = db.query(func.sum(OIL_EXPR))
    oil_q = _apply_date_filter(oil_q, date_from, date_to)
    oil_q = _apply_company_filter(oil_q, company_id)
    total_oil = oil_q.scalar() or 0

    # Средняя обводненность за период
    wc_q = db.query(func.avg(DailyProduction.water_cut))
    wc_q = _apply_date_filter(wc_q, date_from, date_to)
    wc_q = _apply_company_filter(wc_q, company_id)
    avg_water_cut = wc_q.scalar() or 0

    # Число скважин с рапортами за период
    wells_q = db.query(func.count(func.distinct(DailyProduction.well_id)))
    wells_q = _apply_date_filter(wells_q, date_from, date_to)
    wells_q = _apply_company_filter(wells_q, company_id)
    wells_count = wells_q.scalar() or 0

    # Компании: admin — все, manager — своя (1)
    if company_id is None:
        companies_count = db.query(func.count(OilCompany.id)).scalar() or 0
    else:
        companies_count = 1

    return {
        "total_oil": round(total_oil, 1),
        "avg_water_cut": round(avg_water_cut, 1),
        "wells_count": wells_count,
        "companies_count": companies_count,
    }
