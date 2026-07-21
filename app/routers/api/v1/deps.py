"""
Зависимости мобильного API: проверка токена и ролей.

get_current_api_user — аналог мидлвари auth:sanctum в Laravel: достаёт
токен из заголовка Authorization, проверяет подпись и срок, и загружает
сотрудника из БД. Любая ошибка — 401.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee
from app.security import decode_access_token

# tokenUrl нужен, чтобы кнопка Authorize в Swagger знала, куда слать логин.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_api_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Employee:
    """Возвращает сотрудника по валидному Bearer-токену или бросает 401."""
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный или просроченный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if not payload:
        raise credentials_error

    email = payload.get("sub")
    if not email:
        raise credentials_error

    employee = db.query(Employee).filter(Employee.email == email).first()
    if not employee:
        raise credentials_error

    return employee


def require_api_role(*allowed_roles: str):
    """
    Фабрика зависимостей: пускает только указанные роли (иначе 403).

    Использование:
        dependencies=[Depends(require_api_role("admin", "operator"))]
    """

    def checker(user: Employee = Depends(get_current_api_user)) -> Employee:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для этого действия",
            )
        return user

    return checker
