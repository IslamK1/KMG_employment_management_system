"""
Кэширование посчитанных агрегатов дашборда в Redis.

Дашборд пересчитывает тяжёлую агрегацию (сотни скважин × месяцы) на каждый
запрос графика. Кэшируем результат: первый запрос считает и кладёт в Redis,
последующие в течение TTL берут готовое.

Устойчивость к сбоям: если Redis недоступен — тихо считаем без кэша, а не
роняем приложение. Кэш — ускорение, а не критическая зависимость.
"""

import json
import os
from typing import Callable

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Срок жизни кэша: по умолчанию 1 час (критерий — 1-2 часа).
DEFAULT_TTL = int(os.getenv("CACHE_TTL_SECONDS", 3600))

# Префикс ключей — чтобы одним махом сбрасывать только кэш дашборда.
CACHE_PREFIX = "dashboard:"

_client: redis.Redis | None = None


def get_client() -> redis.Redis | None:
    """Ленивое подключение к Redis. Возвращает None, если Redis недоступен."""
    global _client
    if _client is None:
        try:
            _client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
            _client.ping()
        except Exception:
            _client = None
    return _client


def get_or_set(key: str, producer: Callable[[], dict], ttl: int = DEFAULT_TTL) -> dict:
    """
    Отдаёт значение из кэша или вычисляет его через producer() и кэширует.

    Args:
        key: Ключ (без префикса).
        producer: Функция без аргументов, считающая значение при промахе.
        ttl: Время жизни записи в секундах.

    Returns:
        dict: Значение (из кэша или свежевычисленное).
    """
    client = get_client()
    full_key = CACHE_PREFIX + key

    # Попытка достать из кэша
    if client is not None:
        try:
            cached = client.get(full_key)
            if cached is not None:
                return json.loads(cached)
        except Exception:
            client = None  # деградируем до прямого расчёта

    # Промах — считаем
    value = producer()

    # Кладём в кэш (ошибки записи не критичны)
    if client is not None:
        try:
            client.setex(full_key, ttl, json.dumps(value, default=str))
        except Exception:
            pass

    return value


def invalidate() -> None:
    """
    Сбрасывает весь кэш дашборда.

    Вызывается при создании/удалении рапорта: данные изменились, старые
    агрегаты больше не актуальны, ждать истечения TTL не нужно.
    """
    client = get_client()
    if client is None:
        return
    try:
        for k in client.scan_iter(CACHE_PREFIX + "*"):
            client.delete(k)
    except Exception:
        pass
