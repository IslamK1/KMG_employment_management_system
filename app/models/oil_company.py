from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class OilCompany(Base):
    __tablename__ = "oil_companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    region = Column(String, nullable=False)

    employees = relationship("Employee", back_populates="oil_company")
    wells = relationship("Well", back_populates="oil_company")