""" Rate limiting middleware для API """
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
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


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware для обработки rate limiting ошибок."""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except RateLimitExceeded as exc:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "status": 429,
                    "retry_after": exc.retry_after,
                },
            )


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
