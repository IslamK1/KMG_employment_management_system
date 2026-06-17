"""
Функциональные тесты ввода суточного рапорта.

Покрывают два уровня:
  1. Схема DailyProductionCreate — валидация полей (часы, обводненность, плотность).
  2. HTTP-роут POST /productions/create — поведение как у реального пользователя:
     запрет >24 часов и запрет дубликата по (скважина + дата).
"""

from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas import DailyProductionCreate
from app.services import check_duplicate, create_report


#Уровень схемы
class TestSchemaValidation:
    """Валидация на уровне Pydantic-схемы (до попадания в БД)."""

    def test_valid_data_passes(self):
        """Корректные данные проходят валидацию."""
        data = DailyProductionCreate(
            well_id=1,
            date=date(2026, 6, 15),
            working_hours=12.5,
            liquid_volume=150.0,
            water_cut=25.0,
            density=0.86,
        )
        assert data.working_hours == 12.5

    def test_working_hours_24_rejected(self):
        """Ровно 24 часа — запрещено (максимум строго меньше 24)."""
        with pytest.raises(ValidationError):
            DailyProductionCreate(
                well_id=1,
                date=date(2026, 6, 15),
                working_hours=24,
                liquid_volume=150.0,
                water_cut=25.0,
            )

    def test_working_hours_above_24_rejected(self):
        """Больше 24 часов — запрещено."""
        with pytest.raises(ValidationError):
            DailyProductionCreate(
                well_id=1,
                date=date(2026, 6, 15),
                working_hours=25,
                liquid_volume=150.0,
                water_cut=25.0,
            )

    def test_water_cut_above_100_rejected(self):
        """Обводненность больше 100% — запрещено."""
        with pytest.raises(ValidationError):
            DailyProductionCreate(
                well_id=1,
                date=date(2026, 6, 15),
                working_hours=12,
                liquid_volume=150.0,
                water_cut=150.0,
            )

    def test_negative_water_cut_rejected(self):
        """Отрицательная обводненность — запрещено."""
        with pytest.raises(ValidationError):
            DailyProductionCreate(
                well_id=1,
                date=date(2026, 6, 15),
                working_hours=12,
                liquid_volume=150.0,
                water_cut=-5.0,
            )



#Уровень сервисa
class TestCreateReportService:
    """Бизнес-логика create_report и защита от дублей."""

    def _valid_data(self, well_id):
        return DailyProductionCreate(
            well_id=well_id,
            date=date(2026, 6, 15),
            working_hours=12.0,
            liquid_volume=150.0,
            water_cut=25.0,
            density=0.86,
        )

    def test_create_report_success(self, db_session, sample_well):
        """Рапорт успешно создаётся при корректных данных."""
        report, error = create_report(db_session, self._valid_data(sample_well.id))
        assert error is None
        assert report is not None
        assert report.id is not None

    def test_duplicate_rejected(self, db_session, sample_well):
        """Второй рапорт на ту же скважину и дату не создаётся."""
        data = self._valid_data(sample_well.id)
        create_report(db_session, data)

        # повторная попытка с теми же well_id + date
        report, error = create_report(db_session, self._valid_data(sample_well.id))
        assert report is None
        assert error is not None

    def test_check_duplicate(self, db_session, sample_well):
        """check_duplicate видит существующий рапорт и отличает свободную дату."""
        create_report(db_session, self._valid_data(sample_well.id))

        assert check_duplicate(db_session, sample_well.id, date(2026, 6, 15)) is True
        assert check_duplicate(db_session, sample_well.id, date(2026, 6, 16)) is False


# ─────────────────────────── Уровень HTTP ───────────────────────────


class TestHTTPEndpoints:
    """POST /productions/create — поведение как у реального пользователя."""

    def _form(self, well_id, **overrides):
        form = {
            "well_id": well_id,
            "report_date": "2026-06-15",
            "working_hours": 12.0,
            "liquid_volume": 150.0,
            "water_cut": 25.0,
            "density": 0.86,
        }
        form.update(overrides)
        return form

    def test_create_valid_redirects(self, client, sample_well, db_session):
        """Успешное создание редиректит на список рапортов (302)."""
        from app.models import DailyProduction

        resp = client.post(
            "/productions/create",
            data=self._form(sample_well.id),
            follow_redirects=False,
        )
        assert resp.status_code == 302
        assert db_session.query(DailyProduction).count() == 1

    def test_create_over_24_hours_blocked(self, client, sample_well, db_session):
        """Ввод 24 часов отклоняется — рапорт не создаётся."""
        from app.models import DailyProduction

        resp = client.post(
            "/productions/create",
            data=self._form(sample_well.id, working_hours=24),
            follow_redirects=False,
        )
        # роут ловит ошибку валидации и возвращает форму с ошибкой (200), не редирект
        assert resp.status_code == 200
        assert db_session.query(DailyProduction).count() == 0

    def test_create_duplicate_blocked(self, client, sample_well, db_session):
        """Повторный рапорт на ту же дату через HTTP не создаётся."""
        from app.models import DailyProduction

        # первый рапорт — успешно
        client.post(
            "/productions/create",
            data=self._form(sample_well.id),
            follow_redirects=False,
        )
        # дубликат — форма с ошибкой, не редирект
        resp = client.post(
            "/productions/create",
            data=self._form(sample_well.id),
            follow_redirects=False,
        )
        assert resp.status_code == 200
        assert db_session.query(DailyProduction).count() == 1
