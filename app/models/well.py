from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Well(Base):
    __tablename__ = "wells"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    max_drilling_depth = Column(Integer, nullable=False)
    oil_company_id = Column(Integer, ForeignKey("oil_companies.id"), nullable=False)

    oil_company = relationship("OilCompany", back_populates="wells")