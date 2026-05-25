from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    position = Column(String, nullable=True)
    password = Column(String, nullable=False)
    oil_company_id = Column(Integer, ForeignKey("oil_companies.id"), nullable=True)

    oil_company = relationship("OilCompany", back_populates="employees")