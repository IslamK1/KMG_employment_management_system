"""
Модель журнала аудита изменений.

Фиксирует, кто и как изменил показатели суточной добычи (в первую очередь
обводнённость), для информационной и производственной безопасности.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String, nullable=False)          # кто изменил (имя/email)
    action = Column(String, nullable=False)         # что за действие
    well_id = Column(Integer, nullable=True)        # по какой скважине
    report_date = Column(String, nullable=True)     # за какую дату рапорт
    old_value = Column(String, nullable=True)       # было
    new_value = Column(String, nullable=True)       # стало
    message = Column(Text, nullable=False)          # человекочитаемая запись
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
