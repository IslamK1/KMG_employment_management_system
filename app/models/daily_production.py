"""
Модуль модели суточных производственных показателей скважины.
"""

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class DailyProduction(Base):
    """
    Модель суточного производственного рапорта скважины.

    Хранит ежедневные показатели работы скважины.
    Уникальный ключ (well_id + date) защищает от двойного ввода рапорта.

    Attributes:
        id (int): Уникальный идентификатор записи.
        well_id (int): Внешний ключ на скважину.
        date (date): Дата рапорта.
        working_hours (float): Время работы скважины в часах (0-24).
        liquid_volume (float): Объём жидкости в тоннах.
        water_cut (float): Обводненность в процентах (0-100).
        density (float): Плотность нефти (г/см³).
        well (Well): Объект скважины.
    """

    __tablename__ = "daily_productions"

    # Уникальный ключ — защита от двойного ввода рапорта
    __table_args__ = (UniqueConstraint("well_id", "date", name="uq_well_date"),)

    id = Column(Integer, primary_key=True, index=True)
    well_id = Column(Integer, ForeignKey("wells.id"), nullable=False)
    date = Column(Date, nullable=False)
    working_hours = Column(Float, nullable=False)
    liquid_volume = Column(Float, nullable=False)
    water_cut = Column(Float, nullable=False)
    density = Column(Float, nullable=False, default=0.86)

    well = relationship("Well", back_populates="daily_productions")

    @property
    def oil_volume(self) -> float:
        """
        Accessor для расчёта чистой нефти в тоннах.

        Формула: Жидкость * (1 - Вода/100) * Плотность

        Returns:
            float: Объём чистой нефти в тоннах, округлённый до 2 знаков.
        """
        return round(self.liquid_volume * (1 - self.water_cut / 100) * self.density, 2)
