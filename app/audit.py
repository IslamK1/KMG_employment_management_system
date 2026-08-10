"""
Наблюдатель за изменениями суточных рапортов (аналог Laravel Observer).

Механизм: слушаем событие SQLAlchemy `before_flush`. Перед сохранением
изменений проверяем, поменялась ли обводнённость (water_cut) у рапорта,
и если да — незаметно добавляем запись в audit_logs. Бизнес-код при этом
ничего не знает об аудите: наблюдатель срабатывает автоматически, откуда
бы ни пришло изменение (форма редактирования, импорт Excel и т.д.).

Кто изменил (actor) берётся из контекстной переменной, которую роутер
выставляет из данных текущего пользователя.
"""

import contextvars

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from app.models import AuditLog, DailyProduction, Well

# Заставляем SQLAlchemy запоминать старое значение обводнённости при изменении
# (иначе после commit оно "протухает" и в истории нет старого значения).
DailyProduction.water_cut.impl.active_history = True

# Кто выполняет текущее действие (имя/email). Устанавливается в роутере.
_actor_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "audit_actor", default=None
)


def set_actor(name: str | None) -> None:
    """Запомнить, кто выполняет текущий запрос (для записи в аудит)."""
    _actor_var.set(name)


def get_actor() -> str:
    """Текущий actor или 'система', если неизвестен (например, фоновая задача)."""
    return _actor_var.get() or "система"


def _well_name(session: Session, well_id: int) -> str:
    """Имя скважины по id (сессия с autoflush=False — запрос безопасен)."""
    well = session.get(Well, well_id)
    return well.name if well else f"#{well_id}"


@event.listens_for(Session, "before_flush")
def _audit_daily_production(session: Session, flush_context, instances) -> None:
    """
    Пишет в audit_logs изменения суточных рапортов:
      - добавление рапорта;
      - удаление рапорта;
      - изменение обводнённости (water_cut).

    Списки new/deleted/dirty копируем в list(), т.к. внутри цикла добавляем
    в сессию новые объекты (записи аудита) — иначе набор изменится при итерации.
    """
    actor = get_actor()
    logs: list[AuditLog] = []

    # --- Добавление рапорта ---
    for obj in list(session.new):
        if not isinstance(obj, DailyProduction):
            continue
        well_name = _well_name(session, obj.well_id)
        logs.append(
            AuditLog(
                actor=actor,
                action="report_created",
                well_id=obj.well_id,
                report_date=str(obj.date),
                new_value=str(obj.water_cut),
                message=(
                    f"Пользователь {actor} добавил рапорт "
                    f"по скважине {well_name} за дату {obj.date} "
                    f"(обводненность {obj.water_cut}%)"
                ),
            )
        )

    # --- Удаление рапорта ---
    for obj in list(session.deleted):
        if not isinstance(obj, DailyProduction):
            continue
        well_name = _well_name(session, obj.well_id)
        logs.append(
            AuditLog(
                actor=actor,
                action="report_deleted",
                well_id=obj.well_id,
                report_date=str(obj.date),
                old_value=str(obj.water_cut),
                message=(
                    f"Пользователь {actor} удалил рапорт "
                    f"по скважине {well_name} за дату {obj.date}"
                ),
            )
        )

    # --- Изменение обводнённости ---
    for obj in list(session.dirty):
        if not isinstance(obj, DailyProduction):
            continue
        history = inspect(obj).attrs.water_cut.history
        if not history.has_changes():
            continue
        old_value = history.deleted[0] if history.deleted else None
        new_value = history.added[0] if history.added else None
        if old_value is None or new_value is None or old_value == new_value:
            continue
        well_name = _well_name(session, obj.well_id)
        logs.append(
            AuditLog(
                actor=actor,
                action="water_cut_changed",
                well_id=obj.well_id,
                report_date=str(obj.date),
                old_value=str(old_value),
                new_value=str(new_value),
                message=(
                    f"Пользователь {actor} изменил обводненность "
                    f"с {old_value}% на {new_value}% "
                    f"у скважины {well_name} за дату {obj.date}"
                ),
            )
        )

    for log in logs:
        session.add(log)
