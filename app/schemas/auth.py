"""
Pydantic схемы для аутентификации мобильного API.
"""

from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Ответ на успешный вход: токен доступа для мобильного клиента."""

    access_token: str
    token_type: str = "bearer"


class ApiUser(BaseModel):
    """Профиль текущего пользователя (GET /api/v1/auth/me)."""

    email: str
    name: str | None = None
    role: str
    company_id: int | None = None
