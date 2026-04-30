""" Rate limiting middleware для API """
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Инициализация лимитера
limiter = Limiter(key_func=get_remote_address)

# Экспортируем обработчик
__all__ = ['limiter', '_rate_limit_exceeded_handler', 'configure_rate_limiting', 'RATE_LIMITS']

# Конфигурация лимитов
RATE_LIMITS = {
    "default": "100/minute",
    "api": "60/minute",
    "auth": "10/minute",
    "search": "30/minute",
    "feedback": "20/minute",
}


class RateLimitMiddleware:
    """Middleware для обработки rate limiting ошибок."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        try:
            return await self.app(scope, receive, send)
        except RateLimitExceeded as exc:
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "status": 429,
                    "retry_after": exc.retry_after,
                },
            )
            return await response(scope, receive, send)


def configure_rate_limiting(app):
    """Настройка rate limiting для приложения."""
    # Добавляем limiter к app
    app.state.limiter = limiter

    # Добавляем обработчик ошибок rate limit
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    logger.info("Rate limiting configured successfully")
    logger.info(f"Default limit: {RATE_LIMITS['default']}")
    logger.info(f"API limit: {RATE_LIMITS['api']}")
    logger.info(f"Auth limit: {RATE_LIMITS['auth']}")
