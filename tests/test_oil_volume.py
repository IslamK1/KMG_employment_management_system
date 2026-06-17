"""
Unit-тесты расчёта чистой нефти (@property oil_volume).

Проверяют только математику формулы Жидкость * (1 - Вода/100) * Плотность.
База данных не нужна — свойство считается в чистом Python.
"""

from app.models import DailyProduction


def make_report(liquid_volume, water_cut, density):
    """Создаёт объект рапорта в памяти (без сохранения в БД)."""
    return DailyProduction(
        well_id=1,
        liquid_volume=liquid_volume,
        water_cut=water_cut,
        density=density,
    )


def test_oil_volume_basic():
    """450 т жидкости, 20% воды, плотность 0.85 → 306 т нефти."""
    report = make_report(liquid_volume=450, water_cut=20, density=0.85)
    # 450 * (1 - 0.20) * 0.85 = 450 * 0.8 * 0.85 = 306.0
    assert report.oil_volume == 306.0


def test_oil_volume_full_water():
    """100% обводненность → нефти нет совсем."""
    report = make_report(liquid_volume=500, water_cut=100, density=0.86)
    # 500 * (1 - 1) * 0.86 = 0
    assert report.oil_volume == 0.0


def test_oil_volume_no_water():
    """0% воды → вся жидкость учитывается через плотность."""
    report = make_report(liquid_volume=200, water_cut=0, density=0.9)
    # 200 * 1 * 0.9 = 180.0
    assert report.oil_volume == 180.0


def test_oil_volume_rounding():
    """Результат округляется до 2 знаков после запятой."""
    report = make_report(liquid_volume=123.456, water_cut=33.3, density=0.842)
    # 123.456 * (1 - 0.333) * 0.842 = 69.337...
    expected = round(123.456 * (1 - 33.3 / 100) * 0.842, 2)
    assert report.oil_volume == expected


def test_oil_volume_returns_float():
    """Свойство возвращает число с плавающей точкой."""
    report = make_report(liquid_volume=100, water_cut=10, density=0.8)
    assert isinstance(report.oil_volume, float)
