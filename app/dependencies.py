"""
Модуль зависимостей для проверки авторизации.
Содержит вспомогательные функции для защиты маршрутов.
"""

from fastapi import Request
from fastapi.responses import RedirectResponse


def get_current_user(request: Request):
    """
    Возвращает email текущего залогиненного пользователя.
    
    Args:
        request (Request): Объект текущего HTTP запроса.
        
    Returns:
        str | None: Email пользователя если залогинен, иначе None.
    """
    
    return request.session.get("user")



def require_auth(request: Request):
    """
    Проверяет авторизацию пользователя.
    
    Если пользователь не залогинен — возвращает редирект на /login.
    Если залогинен — возвращает его email.
    
    Args:
        request (Request): Объект текущего HTTP запроса.
        
    Returns:
        str | RedirectResponse: Email пользователя или редирект на /login.
    """

    user = request.session.get("user")

    if not user:
        return RedirectResponse(url="/login", status_code=302)

    return user