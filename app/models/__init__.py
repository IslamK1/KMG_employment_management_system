"""
Пакет моделей приложения.
Экспортирует все модели для удобного импорта из других модулей.
"""

from app.models.audit_log import AuditLog as AuditLog
from app.models.daily_production import DailyProduction as DailyProduction
from app.models.employee import Employee as Employee
from app.models.oil_company import OilCompany as OilCompany
from app.models.well import Well as Well

__all__ = ["DailyProduction", "Employee", "OilCompany", "Well", "AuditLog"]
