"""
Пакет сервисов приложения.
Содержит бизнес-логику для работы с сотрудниками, авторизацией и рапортами.
"""

from app.services.auth_service import authenticate_employee as authenticate_employee

from app.services.dashboard_service import (
    get_oil_dynamics as get_oil_dynamics,
    get_top_companies as get_top_companies,
    get_water_cut_by_company as get_water_cut_by_company,
    get_well_types_distribution as get_well_types_distribution,
)

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

from app.services.dashboard_service import get_kpis as get_kpis

from app.services.company_service import (
    create_company as create_company,
    delete_company as delete_company,
    get_companies_paginated as get_companies_paginated,
    get_company_by_id as get_company_by_id,
    update_company as update_company,
)

from app.services.excel_service import (
    build_import_template as build_import_template,
    export_monthly_summary as export_monthly_summary,
    import_productions as import_productions,
)

from app.services.well_service import (
    create_well as create_well,
    delete_well as delete_well,
    get_well_by_id as get_well_by_id,
    get_wells_paginated as get_wells_paginated,
    update_well as update_well,
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