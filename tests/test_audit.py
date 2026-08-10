"""
Тесты аудита изменений рапортов (задание 15).

Проверяют, что смена обводнённости пишется в audit_logs с корректными
значениями и автором, а изменение других полей — нет.
"""

from datetime import date

from app import audit
from app.models import AuditLog, DailyProduction, OilCompany, Well


def _make_report(db, water_cut=15.0):
    company = OilCompany(name="Компания", region="Регион")
    db.add(company)
    db.commit()
    well = Well(
        name="Скважина-1",
        type="нефтяная",
        max_drilling_depth=3000,
        oil_company_id=company.id,
    )
    db.add(well)
    db.commit()
    report = DailyProduction(
        well_id=well.id,
        date=date(2026, 1, 10),
        working_hours=12,
        liquid_volume=100,
        water_cut=water_cut,
        density=0.86,
    )
    db.add(report)
    db.commit()
    # Хелпер сам создаёт рапорт (это тоже пишется в аудит) — чистим лог,
    # чтобы каждый тест видел только записи от своего действия.
    db.query(AuditLog).delete()
    db.commit()
    return report, well


def test_water_cut_change_creates_audit_log(db_session):
    report, well = _make_report(db_session, water_cut=15.0)

    audit.set_actor("Иван Оператор")
    report.water_cut = 18.0
    db_session.commit()

    logs = db_session.query(AuditLog).all()
    assert len(logs) == 1
    log = logs[0]
    assert log.actor == "Иван Оператор"
    assert log.action == "water_cut_changed"
    assert log.old_value == "15.0"
    assert log.new_value == "18.0"
    assert log.well_id == well.id
    assert "изменил обводненность" in log.message
    assert "15.0%" in log.message
    assert "18.0%" in log.message
    assert well.name in log.message


def test_no_log_when_water_cut_unchanged(db_session):
    report, _ = _make_report(db_session, water_cut=20.0)

    audit.set_actor("Иван")
    report.working_hours = 10  # меняем другое поле, не обводнённость
    db_session.commit()

    assert db_session.query(AuditLog).count() == 0


def test_actor_defaults_to_system(db_session):
    report, _ = _make_report(db_session, water_cut=10.0)

    audit.set_actor(None)  # автор неизвестен (например, фоновая задача)
    report.water_cut = 12.0
    db_session.commit()

    log = db_session.query(AuditLog).first()
    assert log is not None
    assert log.actor == "система"


def test_create_report_creates_audit_log(db_session):
    company = OilCompany(name="Компания", region="Регион")
    db_session.add(company)
    db_session.commit()
    well = Well(
        name="Скважина-2",
        type="нефтяная",
        max_drilling_depth=3000,
        oil_company_id=company.id,
    )
    db_session.add(well)
    db_session.commit()

    audit.set_actor("Оператор")
    report = DailyProduction(
        well_id=well.id,
        date=date(2026, 1, 11),
        working_hours=10,
        liquid_volume=50,
        water_cut=25,
        density=0.86,
    )
    db_session.add(report)
    db_session.commit()

    log = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "report_created")
        .first()
    )
    assert log is not None
    assert log.actor == "Оператор"
    assert "добавил рапорт" in log.message
    assert well.name in log.message


def test_delete_report_creates_audit_log(db_session):
    report, well = _make_report(db_session, water_cut=30.0)

    audit.set_actor("Админ")
    db_session.delete(report)
    db_session.commit()

    log = (
        db_session.query(AuditLog)
        .filter(AuditLog.action == "report_deleted")
        .first()
    )
    assert log is not None
    assert log.actor == "Админ"
    assert "удалил рапорт" in log.message
    assert well.name in log.message
