"""
JWT-токены для мобильного API (аналог Laravel Sanctum в мире FastAPI).

Access-токен подписывается симметричным ключом (HS256) и содержит email,
роль и компанию пользователя. Токен stateless — сервер не хранит сессий,
поэтому подходит для мобильного клиента на слабом 3G: одно подключение на
вход, дальше каждый запрос несёт заголовок Authorization: Bearer <token>.
"""

import os
from datetime import datetime, timedelta, timezone

import jwt

# Ключ подписи. В Docker задаётся переменной окружения JWT_SECRET;
# значение по умолчанию — только для локальной разработки.
SECRET_KEY = os.getenv("JWT_SECRET", "dev-insecure-change-me-in-production")
ALGORITHM = "HS256"

# Длинный срок жизни токена: оператор на буровой не должен часто
# пере-логиниться при плохой связи. По умолчанию 7 дней.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))


def create_access_token(data: dict, expires_minutes: int | None = None) -> str:
    """
    Создаёт подписанный JWT.

    Args:
        data (dict): Полезная нагрузка (обычно sub=email, role, company_id).
        expires_minutes (int | None): Срок жизни; по умолчанию 7 дней.

    Returns:
        str: Закодированный токен.
    """
    to_encode = data.copy()
    minutes = expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """
    Проверяет подпись и срок действия токена.

    Returns:
        dict | None: Полезная нагрузка, если токен валиден, иначе None.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
