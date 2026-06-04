"""
Модуль модели сотрудника.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Employee(Base):
    """
    Модель сотрудника.

    Представляет сотрудника компании в системе управления.
    Используется как для авторизации так и для управления персоналом.

    Aттрибуты:
        id (int): Уникальный идентификатор сотрудника.
        name (str): Полное имя сотрудника.
        email (str): Email адрес — используется для входа в систему.
        position (str): Должность сотрудника.
        password (str): Хэш пароля (bcrypt).
        oil_company_id (int): Внешний ключ на нефтяную компанию.
        oil_company (OilCompany): Объект нефтяной компании.
    """

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    position = Column(String, nullable=True)
    password = Column(String, nullable=False)
    oil_company_id = Column(Integer, ForeignKey("oil_companies.id"), nullable=True)

    oil_company = relationship("OilCompany", back_populates="employees")
