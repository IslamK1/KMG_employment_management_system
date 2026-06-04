"""
Модуль модели скважины.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Well(Base):
    """
    Модель буровой скважины.

    Представляет буровую скважину принадлежащую нефтяной компании.

    Aттрибуты:
        id (int): Уникальный идентификатор скважины.
        name (str): Название скважины.
        type (str): Тип скважины (нефтяная, газовая, разведочная, нагнетательная).
        max_drilling_depth (int): Максимальная глубина бурения в метрах.
        oil_company_id (int): Внешний ключ на нефтяную компанию.
        oil_company (OilCompany): Объект нефтяной компании.
        daily_productions (list): Список суточных показателей скважины.
    """

    __tablename__ = "wells"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    max_drilling_depth = Column(Integer, nullable=False)
    oil_company_id = Column(Integer, ForeignKey("oil_companies.id"), nullable=False)

    oil_company = relationship("OilCompany", back_populates="wells")
    daily_productions = relationship("DailyProduction", back_populates="well")
