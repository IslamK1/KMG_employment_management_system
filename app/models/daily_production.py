"""
Модуль модели суточных производственных показателей.
"""

from sqlalchemy import Column, Date, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class DailyProduction(Base): 
    """
    Модель суточных производственных показателей скважины.
    
    Хранит данные о добыче нефти по каждой скважине за каждый день.
    Используется для построения аналитических дашбордов.
    
    Aттрибуты:
        id (int): Уникальный идентификатор записи.
        date (date): Дата производственного показателя.
        well_id (int): Внешний ключ на скважину.
        oil_volume (float): Объём добытой нефти в тоннах за сутки.
        well (Well): Объект скважины.
    """

    __tablename__ = "daily_productions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    well_id = Column(Integer, ForeignKey("wells.id"), nullable=False)
    oil_volume = Column(Float, nullable=False)

    well = relationship("Well", back_populates="daily_productions")