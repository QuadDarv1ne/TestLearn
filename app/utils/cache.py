""" Кэширование для оптимизации производительности """
import logging
import time
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class Cache:
    """Простой in-memory кэш с TTL."""

    def __init__(self, default_ttl: int = 300):
        """
        Инициализация кэша.

        Args:
            default_ttl: Время жизни записи в секундах (по умолчанию 5 минут)
        """
        self._cache: Dict[str, tuple[Any, float]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """
        Получить значение из кэша.

        Args:
            key: Ключ для получения

        Returns:
            Значение или None если устарело или не существует
        """
        if key not in self._cache:
            return None

        value, expiry = self._cache[key]
        if time.time() > expiry:
            del self._cache[key]
            logger.debug(f"Cache miss (expired): {key}")
            return None

        logger.debug(f"Cache hit: {key}")
        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Сохранить значение в кэш.

        Args:
            key: Ключ для сохранения
            value: Значение для сохранения
            ttl: Время жизни в секундах (использует default_ttl если не указано)
        """
        ttl = ttl or self.default_ttl
        expiry = time.time() + ttl
        self._cache[key] = (value, expiry)
        logger.debug(f"Cache set: {key} (TTL: {ttl}s)")

    def delete(self, key: str) -> bool:
        """
        Удалить значение из кэша.

        Args:
            key: Ключ для удаления

        Returns:
            True если удалено, False если не существовало
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache deleted: {key}")
            return True
        return False

    def clear(self) -> None:
        """Очистить весь кэш."""
        self._cache.clear()
        logger.info("Cache cleared")

    def cleanup(self) -> int:
        """
        Удалить все устаревшие записи.

        Returns:
            Количество удаленных записей
        """
        now = time.time()
        expired_keys = [
            key for key, (_, expiry) in self._cache.items() if now > expiry
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

        return len(expired_keys)


# Глобальный экземпляр кэша
cache = Cache(default_ttl=300)


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Декоратор для кэширования результатов функций.

    Args:
        ttl: Время жизни кэша в секундах
        key_prefix: Префикс для ключей кэша

    Example:
        @cached(ttl=60, key_prefix="categories")
        def get_all_categories():
            return db.query(Category).all()
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            # Создаем уникальный ключ
            key_parts = [key_prefix, func.__name__]
            if args:
                key_parts.extend(str(arg) for arg in args)
            if kwargs:
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))

            key = ":".join(key_parts)

            # Пытаемся получить из кэша
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value

            # Вызываем функцию и кэшируем результат
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)

            return result

        return wrapper

    return decorator


@cached(ttl=300, key_prefix="db")
def get_categories_from_db(db_session) -> list:
    """Кэшированная функция получения категорий из БД."""
    from sqlalchemy import inspect

    from app.db.models import Category

    # Проверяем есть ли данные в таблице
    inspector = inspect(db_session.bind)
    tables = inspector.get_table_names()

    if "category" not in tables and "categories" not in tables:
        return []

    categories = db_session.query(Category).order_by(Category.name).all()
    return [
        {"id": cat.id, "name": cat.name, "slug": cat.slug} for cat in categories
    ]


@cached(ttl=60, key_prefix="stats")
def get_platform_stats(db_session) -> dict:
    """Кэшированная функция получения статистики платформы."""
    from app.db.models import Category, GlossaryTerm, Question, Quiz, Topic

    stats = {
        "categories": db_session.query(Category).count(),
        "topics": db_session.query(Topic).count(),
        "quizzes": db_session.query(Quiz).count(),
        "questions": db_session.query(Question).count(),
        "glossary_terms": db_session.query(GlossaryTerm).count(),
    }

    return stats
