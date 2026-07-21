"""
Аутентификация мобильного API (/api/v1/auth).

POST /login — обменивает email+пароль на JWT-токен.
GET  /me    — профиль текущего пользователя по токену.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee
from app.routers.api.v1.deps import get_current_api_user
from app.schemas import ApiUser, TokenResponse
from app.security import create_access_token
from app.services.auth_service import authenticate_employee

router = APIRouter(prefix="/auth", tags=["API v1 — Аутентификация"])


@router.post("/login", response_model=TokenResponse)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Вход по email и паролю, выдача токена.

    В форме OAuth2 поле называется `username` — сюда мобильный клиент
    передаёт email сотрудника.
    """
    employee = authenticate_employee(db, form.username, form.password)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        {
            "sub": employee.email,
            "role": employee.role,
            "company_id": employee.oil_company_id,
        }
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=ApiUser)
def me(user: Employee = Depends(get_current_api_user)):
    """Профиль владельца токена — удобно для проверки авторизации в приложении."""
    return ApiUser(
        email=user.email,
        name=user.name,
        role=user.role,
        company_id=user.oil_company_id,
    )
