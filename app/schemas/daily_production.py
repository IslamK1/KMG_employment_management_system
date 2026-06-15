"""
Pydantic схемы для валидации суточных производственных показателей.
"""

from datetime import date

from pydantic import BaseModel, Field, field_validator


class DailyProductionCreate(BaseModel):
    """
    Схема для создания суточного рапорта.

    Содержит строгие валидации всех полей.

    Attributes:
        well_id (int): ID скважины.
        date (date): Дата рапорта.
        working_hours (float): Время работы 0-24 часа.
        liquid_volume (float): Объём жидкости в тоннах.
        water_cut (float): Обводненность 0-100%.
        density (float): Плотность нефти 0.7-1.0 г/см³.
    """

    well_id: int
    date: date
    working_hours: float = Field(..., ge=0, lt=24, description="Время работы 0-24 часа")
    liquid_volume: float = Field(..., gt=0, description="Объём жидкости в тоннах")
    water_cut: float = Field(..., ge=0, le=100, description="Обводненность 0-100%")
    density: float = Field(default=0.86, ge=0.7, le=1.0, description="Плотность нефти")

    @field_validator("working_hours")
    @classmethod
    def validate_working_hours(cls, v: float) -> float:
        """Проверяет что время работы в диапазоне 0-24 часа."""
        if not 0 <= v < 24:
            raise ValueError("Время работы должно быть от 0 до 24 часов")
        return v

    @field_validator("water_cut")
    @classmethod
    def validate_water_cut(cls, v: float) -> float:
        """Проверяет что обводненность в диапазоне 0-100%."""
        if not 0 <= v <= 100:
            raise ValueError("Обводненность должна быть от 0 до 100%")
        return v
