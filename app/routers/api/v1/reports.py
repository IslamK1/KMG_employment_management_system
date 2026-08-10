"""
Мобильный API суточных рапортов (/api/v1).

POST /reports — основной эндпоинт: оператор с телефона отправляет
                суточный рапорт по скважине.
GET  /wells   — список скважин пользователя (чтобы приложение показало
                выпадающий список для выбора).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.audit import set_actor
from app.database import get_db
from app.models import Employee
from app.routers.api.v1.deps import get_current_api_user
from app.schemas import DailyProductionCreate, DailyProductionRead
from app.services import daily_production_service as svc

router = APIRouter(tags=["API v1 — Рапорты"])


@router.get("/wells")
def my_wells(
    user: Employee = Depends(get_current_api_user),
    db: Session = Depends(get_db),
):
    """
    Скважины, доступные пользователю.

    Админ видит все, остальные — только скважины своей компании.
    Мобильное приложение использует это для выбора скважины в форме.
    """
    if user.role == "admin":
        wells = svc.get_all_wells(db)
    elif user.oil_company_id:
        wells = svc.get_wells_for_company(db, user.oil_company_id)
    else:
        wells = []
    return [{"id": w.id, "name": w.name, "type": w.type} for w in wells]


@router.post(
    "/reports",
    response_model=DailyProductionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_report(
    payload: DailyProductionCreate,
    user: Employee = Depends(get_current_api_user),
    db: Session = Depends(get_db),
):
    """
    Создать суточный рапорт с мобильного клиента.

    Проверки по слоям:
      - токен (get_current_api_user) — иначе 401;
      - Pydantic-схема — некорректные значения дают 422 автоматически;
      - привязка скважины к компании — оператор не запишет чужую (403);
      - защита от двойного ввода в сервисе — дубль даёт 409.
    """
    # Не-админ может писать только по скважине своей компании.
    if user.role != "admin":
        if not user.oil_company_id or not svc.well_belongs_to_company(
            db, payload.well_id, user.oil_company_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Скважина не принадлежит вашей компании",
            )

    set_actor(user.name or user.email)
    report, error = svc.create_report(db, payload)
    if error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error)

    return report
