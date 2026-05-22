# Request — объект текущего запроса, содержит сессию, заголовки и тд
from fastapi import Request

# RedirectResponse — HTTP ответ который говорит браузеру перейти на другой URL
from fastapi.responses import RedirectResponse


# Просто читает сессию и возвращает email текущего пользователя
# Возвращает email если залогинен, None если нет
# Используется когда нужно просто узнать кто залогинен (без редиректа)
def get_current_user(request: Request):
    # .get() безопаснее чем ["user"] — не выбросит ошибку если ключа нет
    return request.session.get("user")


# Охранник маршрутов — проверяет залогинен ли пользователь
# Если НЕ залогинен — возвращает редирект на /login
# Если залогинен — возвращает email пользователя
# Вынесено сюда чтобы не дублировать эту логику в каждом роуте (принцип DRY)
def require_auth(request: Request):
    user = request.session.get("user")

    # Пользователь не залогинен — отправляем на страницу входа
    # 302 — стандартный код временного редиректа, браузер автоматически переходит
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # Пользователь залогинен — возвращаем его email
    return user