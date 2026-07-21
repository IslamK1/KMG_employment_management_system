"""
Модуль зависимостей для проверки авторизации и ролей.

Ролевая модель (аналог Laravel Gates/Policies):
  - admin    — полный доступ, создаёт компании и назначает менеджеров
  - manager  — дашборд и скважины своей компании
  - operator — только рапорты по скважинам своей компании

Роль и компания пользователя хранятся в сессии при входе.

Важно: чтобы зависимость реально прерывала запрос и делала редирект,
она должна ВЫБРАСЫВАТЬ исключение. Если просто вернуть RedirectResponse,
FastAPI проигнорирует его (значение уйдёт как результат зависимости).
Поэтому используем HTTPException со статусом 302 и заголовком Location —
браузер увидит редирект.
"""

from fastapi import HTTPException, Request, status

from app.policies import AccessPolicy


def get_policy(request: Request) -> AccessPolicy:
    """
    Возвращает объект политики доступа для текущего пользователя.

    Единая точка получения ролевых прав в роутерах:
        policy = get_policy(request)
        if not policy.can_access_dashboard(): ...
    """
    return AccessPolicy(get_current_user(request))


def _redirect(url: str) -> HTTPException:
    """Создаёт исключение-редирект (302 + заголовок Location)."""
    return HTTPException(
        status_code=status.HTTP_302_FOUND,
        detail="redirect",
        headers={"Location": url},
    )


def get_current_user(request: Request) -> dict | None:
    """
    Возвращает данные текущего пользователя из сессии.

    Returns:
        dict | None: {email, name, role, company_id} или None если не залогинен.
    """
    email = request.session.get("user")
    if not email:
        return None
    return {
        "email": email,
        "name": request.session.get("user_name"),
        "role": request.session.get("user_role"),
        "company_id": request.session.get("user_company_id"),
    }


def require_auth(request: Request):
    """
    Проверяет что пользователь залогинен, иначе редиректит на /login.

    Returns:
        str: Email пользователя (если залогинен).

    Raises:
        HTTPException: 302 на /login, если не залогинен.
    """
    user = request.session.get("user")
    if not user:
        raise _redirect("/login")
    return user


def require_role(*allowed_roles: str):
    """
    Фабрика зависимостей: пускает только пользователей с нужной ролью.

    Использование в роуте:
        dependencies=[Depends(require_role("admin", "manager"))]

    Args:
        *allowed_roles: Роли, которым разрешён доступ.

    Returns:
        Функция-зависимость для Depends().
    """

    def checker(request: Request):
        if not request.session.get("user"):
            raise _redirect("/login")
        role = request.session.get("user_role")
        if role not in allowed_roles:
            # нет прав — на страницу рапортов (доступна всем ролям)
            raise _redirect("/productions/")
        return role

    return checker
