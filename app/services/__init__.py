"""
Пакет сервисов приложения.
Содержит бизнес-логику для работы с сотрудниками, авторизацией и рапортами.
"""

from app.services.auth_service import authenticate_employee as authenticate_employee
from app.services.daily_production_service import (
    check_duplicate as check_duplicate,
    create_report as create_report,
    delete_report as delete_report,
    get_all_reports as get_all_reports,
    get_all_wells as get_all_wells,
    get_report_by_id as get_report_by_id,
    get_reports_paginated as get_reports_paginated,
)
from app.services.employee_service import (
    create_employee as create_employee,
    delete_employee as delete_employee,
    get_all_companies as get_all_companies,
    get_all_employees as get_all_employees,
    get_employee_by_id as get_employee_by_id,
    get_employees_paginated as get_employees_paginated,
    update_employee as update_employee,
)

__all__ = [
    "authenticate_employee",
    "get_all_employees",
    "get_employees_paginated",
    "get_employee_by_id",
    "get_all_companies",
    "create_employee",
    "update_employee",
    "delete_employee",
    "get_all_reports",
    "get_reports_paginated",
    "get_report_by_id",
    "create_report",
    "delete_report",
    "get_all_wells",
    "check_duplicate",
]