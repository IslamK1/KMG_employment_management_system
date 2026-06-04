"""
Модуль модели нефтяной компании.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class OilCompany(Base):
    """
    Модель нефтяной компании.
    
    Представляет нефтяную компанию в системе.
    Является родительской сущностью для сотрудников и скважин.
    
    Aттрибуты:
        id (int): Уникальный идентификатор компании.
        name (str): Название компании.
        region (str): Регион где работает компания.
        employees (list): Список сотрудников компании.
        wells (list): Список скважин компании.
    """

    __tablename__ = "oil_companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    region = Column(String, nullable=False)

    employees = relationship("Employee", back_populates="oil_company")
    wells = relationship("Well", back_populates="oil_company")