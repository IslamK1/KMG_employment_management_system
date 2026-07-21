"""
Класс разграничения доступа по ролям (аналог Laravel Policy).

Вся ролевая логика собрана здесь: и проверки прав (что пользователю
можно), и разграничение данных (какие данные он видит). Роутеры и
шаблоны не проверяют роли сами, а спрашивают у этого класса — так
логика в одном месте, а не разбросана по контроллерам.

Роли:
  admin    — полный доступ ко всему холдингу
  manager  — дашборд и скважины ТОЛЬКО своей компании
  operator — рапорты только по скважинам своей компании,
             без доступа к дашборду и отчётам холдинга
"""

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models import DailyProduction, Well

# сколько дней рапорт доступен для редактирования (потом «замораживается»)
REPORT_EDIT_DAYS = 7


class AccessPolicy:
    """
    Инкапсулирует правила доступа и разграничения данных по ролям.

    Принимает данные текущего пользователя (dict из сессии):
    {email, name, role, company_id}. Все методы отвечают на вопрос
    «можно ли» или «какие данные показать» для этого пользователя.
    """

    def __init__(self, user: dict | None):
        """
        Args:
            user (dict | None): Данные пользователя из сессии или None.
        """
        self.user = user or {}
        self.role = self.user.get("role")
        self.company_id = self.user.get("company_id")

    # ─────────── проверки роли (аналог Gates) ───────────

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def is_manager(self) -> bool:
        return self.role == "manager"

    @property
    def is_operator(self) -> bool:
        return self.role == "operator"

    def can_manage_companies(self) -> bool:
        """Создание/редактирование компаний — только admin."""
        return self.is_admin

    def can_manage_employees(self) -> bool:
        """Сотрудники и назначение ролей — только admin."""
        return self.is_admin

    def can_manage_wells(self) -> bool:
        """Управление скважинами — admin и manager."""
        return self.role in ("admin", "manager")

    def can_access_dashboard(self) -> bool:
        """Дашборд и графические отчёты — admin и manager (operator нельзя)."""
        return self.role in ("admin", "manager")

    def can_export_reports(self) -> bool:
        """Экспорт отчётов холдинга — admin и manager."""
        return self.role in ("admin", "manager")

    # ─────────── разграничение данных ───────────

    def visible_company_id(self) -> int | None:
        """
        Компания, данные которой видит пользователь.

        admin — None (весь холдинг), manager/operator — своя компания.
        """
        if self.is_admin:
            return None
        return self.company_id

    def wells_query(self, db: Session):
        """
        Запрос скважин с учётом роли: admin видит все, остальные — свои.

        Returns:
            Query: SQLAlchemy-запрос (не .all(), чтобы можно было
                   добавить пагинацию поверх).
        """
        query = db.query(Well)
        company_id = self.visible_company_id()
        if company_id is not None:
            query = query.filter(Well.oil_company_id == company_id)
        return query

    def wells_for_form(self, db: Session) -> list:
        """Скважины для формы выбора: admin — все, иначе только своей компании."""
        return self.wells_query(db).all()

    def reports_query(self, db: Session):
        """
        Запрос рапортов с учётом роли.

        admin видит все рапорты холдинга; manager и operator — только
        рапорты по скважинам своей компании.

        Returns:
            Query: SQLAlchemy-запрос (без .all(), чтобы навесить пагинацию).
        """
        query = db.query(DailyProduction)
        company_id = self.visible_company_id()
        if company_id is not None:
            from sqlalchemy import select

            own_wells = select(Well.id).where(Well.oil_company_id == company_id)
            query = query.filter(DailyProduction.well_id.in_(own_wells))
        return query

    def can_view_report(self, db: Session, report: DailyProduction) -> bool:
        """
        Может ли пользователь смотреть этот рапорт.

        admin — любой; manager/operator — только по скважине своей компании.
        Защита от просмотра чужого рапорта по прямому URL.
        """
        if self.is_admin:
            return True
        if report is None:
            return False
        well = db.query(Well).filter(Well.id == report.well_id).first()
        return well is not None and well.oil_company_id == self.company_id

    # ─────────── проверки на конкретных объектах ───────────

    def can_manage_well(self, db: Session, well_id: int) -> bool:
        """
        Может ли пользователь редактировать/просматривать эту скважину.

        admin — любую; manager — только скважину своей компании.
        Защита от доступа к чужой скважине по прямому URL.
        """
        if self.is_admin:
            return True
        if not self.can_manage_wells():
            return False
        well = db.query(Well).filter(Well.id == well_id).first()
        return well is not None and well.oil_company_id == self.company_id

    def can_assign_company(self, company_id: int) -> bool:
        """
        Может ли пользователь привязать скважину к указанной компании.

        admin — к любой; manager — только к своей (нельзя увести скважину
        в чужую компанию через форму).
        """
        if self.is_admin:
            return True
        return company_id == self.company_id

    def can_create_report_for_well(self, db: Session, well_id: int) -> bool:
        """
        Может ли пользователь внести рапорт по этой скважине.

        Ограничение по компании применяется только к operator: он вносит
        рапорты лишь по скважинам своей компании. Admin и manager (и любой
        не-operator) — без этого ограничения.
        """
        if not self.is_operator:
            return True
        well = db.query(Well).filter(Well.id == well_id).first()
        if not well:
            return False
        return well.oil_company_id == self.company_id

    def can_delete_report(self, db: Session, report: DailyProduction) -> bool:
        """
        Может ли пользователь удалить/редактировать рапорт.

        Проверяются два условия для не-админа:
          1) рапорт относится к скважине его компании;
          2) рапорт не старше REPORT_EDIT_DAYS дней.
        """
        if self.is_admin:
            return True
        if report is None:
            return False
        if not self.can_view_report(db, report):
            return False
        return not self.is_report_locked(report.date)

    @staticmethod
    def is_report_locked(report_date, edit_days: int = REPORT_EDIT_DAYS) -> bool:
        """Старше ли рапорт разрешённого срока редактирования."""
        return report_date < date.today() - timedelta(days=edit_days)
