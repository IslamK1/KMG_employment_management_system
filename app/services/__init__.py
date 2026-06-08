"""
Пакет сервисов приложения.
"""

from app.services.auth_service import authenticate_employee as authenticate_employee
from app.services.daily_production_service import (
    check_duplicate as check_duplicate,
)
from app.services.daily_production_service import (
    create_report as create_report,
)
from app.services.daily_production_service import (
    delete_report as delete_report,
)
from app.services.daily_production_service import (
    get_all_reports as get_all_reports,
)
from app.services.daily_production_service import (
    get_all_wells as get_all_wells,
)
from app.services.daily_production_service import (
    get_report_by_id as get_report_by_id,
)
from app.services.employee_service import (
    create_employee as create_employee,
)
from app.services.employee_service import (
    delete_employee as delete_employee,
)
from app.services.employee_service import (
    get_all_companies as get_all_companies,
)
from app.services.employee_service import (
    get_all_employees as get_all_employees,
)
from app.services.employee_service import (
    get_employee_by_id as get_employee_by_id,
)
from app.services.employee_service import (
    update_employee as update_employee,
)

__all__ = [
    "authenticate_employee",
    "get_all_employees",
    "get_employee_by_id",
    "get_all_companies",
    "create_employee",
    "update_employee",
    "delete_employee",
    "get_all_reports",
    "get_report_by_id",
    "create_report",
    "delete_report",
    "get_all_wells",
    "check_duplicate",
]
