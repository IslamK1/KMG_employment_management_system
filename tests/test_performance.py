"""
Тесты производительности (задание 14).

1. Eager Loading: число SQL-запросов при выборке рапортов не зависит от их
   количества (N+1 устранён).
2. Redis-кэш: get_or_set вычисляет значение один раз, invalidate его сбрасывает.
"""

from datetime import date, timedelta

from sqlalchemy import event

from app import cache
from app.models import DailyProduction, OilCompany, Well
from app.services import get_all_reports


class QueryCounter:
    """Считает количество SQL-запросов к движку внутри блока with."""

    def __init__(self, engine):
        self.engine = engine
        self.count = 0

    def _callback(self, *args):
        self.count += 1

    def __enter__(self):
        event.listen(self.engine, "after_cursor_execute", self._callback)
        return self

    def __exit__(self, *args):
        event.remove(self.engine, "after_cursor_execute", self._callback)


def _seed_reports(db, n_reports: int):
    """Создаёт 1 компанию, 2 скважины и n_reports рапортов по разным датам."""
    company = OilCompany(name="Компания", region="Регион")
    db.add(company)
    db.commit()

    wells = []
    for i in range(2):
        w = Well(
            name=f"Скважина-{i}",
            type="нефтяная",
            max_drilling_depth=3000,
            oil_company_id=company.id,
        )
        db.add(w)
        wells.append(w)
    db.commit()

    base_day = date(2026, 1, 1)
    for i in range(n_reports):
        db.add(
            DailyProduction(
                well_id=wells[i % 2].id,
                date=base_day + timedelta(days=i),
                working_hours=12,
                liquid_volume=100,
                water_cut=20,
                density=0.86,
            )
        )
    db.commit()


def _count_queries_loading_reports(db):
    """Загружает рапорты и трогает well.oil_company, считая SQL-запросы."""
    engine = db.get_bind()
    db.expire_all()  # сбросить кэш сессии, чтобы мерить честно
    with QueryCounter(engine) as qc:
        reports = get_all_reports(db)
        for r in reports:
            _ = r.well.name
            _ = r.well.oil_company.name
    return qc.count


def test_eager_loading_kills_n_plus_1(db_session):
    """Запросов ровно 3 (рапорты + скважины + компании), а не 1+N."""
    _seed_reports(db_session, n_reports=6)
    queries = _count_queries_loading_reports(db_session)
    # 1 запрос на рапорты + 1 на скважины (IN) + 1 на компании (IN)
    assert queries == 3


def test_query_count_independent_of_report_count(db_session):
    """Ключевое: при большем числе рапортов число запросов НЕ растёт."""
    _seed_reports(db_session, n_reports=25)
    queries = _count_queries_loading_reports(db_session)
    assert queries == 3  # столько же, сколько для 6 рапортов — N+1 устранён


# ---------- Redis-кэш ----------


class FakeRedis:
    """Минимальный in-memory заменитель Redis для тестов."""

    def __init__(self):
        self.store: dict[str, str] = {}

    def get(self, key):
        return self.store.get(key)

    def setex(self, key, ttl, value):
        self.store[key] = value

    def scan_iter(self, pattern):
        prefix = pattern.rstrip("*")
        return [k for k in list(self.store) if k.startswith(prefix)]

    def delete(self, key):
        self.store.pop(key, None)


def test_get_or_set_computes_once(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(cache, "get_client", lambda: fake)

    calls = {"n": 0}

    def producer():
        calls["n"] += 1
        return {"value": 42}

    first = cache.get_or_set("k1", producer)
    second = cache.get_or_set("k1", producer)

    assert first == second == {"value": 42}
    assert calls["n"] == 1  # второй раз взято из кэша, producer не вызван


def test_invalidate_clears_cache(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(cache, "get_client", lambda: fake)

    cache.get_or_set("k1", lambda: {"a": 1})
    cache.get_or_set("k2", lambda: {"b": 2})
    assert fake.store  # что-то закэшировано

    cache.invalidate()
    assert fake.store == {}  # всё сброшено


def test_cache_survives_redis_down(monkeypatch):
    """Если Redis недоступен (get_client None) — просто считаем без падения."""
    monkeypatch.setattr(cache, "get_client", lambda: None)
    result = cache.get_or_set("k", lambda: {"ok": True})
    assert result == {"ok": True}
