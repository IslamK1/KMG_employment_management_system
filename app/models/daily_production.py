from sqlalchemy import Column, Date, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class DailyProduction(Base): 
    __tablename__ = "daily_productions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    well_id = Column(Integer, ForeignKey("wells.id"), nullable=False)
    oil_volume = Column(Float, nullable=False)

    well = relationship("Well", back_populates="daily_productions")