""" Rate limiting middleware для API """
import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

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
        print(f"[RATE LIMIT MIDDLEWARE] Dispatch called for {request.url}")  # DEBUG
        try:
            result = await call_next(request)
            print("[RATE LIMIT MIDDLEWARE] call_next succeeded")  # DEBUG
            return result
        except RateLimitExceeded as exc:
            print(f"[RATE LIMIT MIDDLEWARE] Caught RateLimitExceeded: {exc}")  # DEBUG
            print(f"[RATE LIMIT MIDDLEWARE] exc.detail: {exc.detail}")  # DEBUG
            print(f"[RATE LIMIT MIDDLEWARE] exc.retry_after: {exc.retry_after}")  # DEBUG
            print("[RATE LIMIT MIDDLEWARE] This is the except block!")  # DEBUG
            response_content = {
                "detail": "Too many requests. Please try again later.",
                "status": 429,
                "retry_after": exc.retry_after,
            }
            print(f"[RATE LIMIT MIDDLEWARE] response_content: {response_content}")  # DEBUG
            response = JSONResponse(
                status_code=429,
                content=response_content,
            )
            print(f"[RATE LIMIT MIDDLEWARE] response body: {response.body}")  # DEBUG
            print(f"[RATE LIMIT MIDDLEWARE] Returning response: {response.body}")  # DEBUG
            return response
        except Exception as exc:
            print(f"[RATE LIMIT MIDDLEWARE] Caught other exception: {type(exc).__name__}: {exc}")  # DEBUG
            # Re-raise so that FastAPI can handle it or it propagates
            raise


def configure_rate_limiting(app):
    """Настройка rate limiting для приложения."""
    print("[RATE LIMIT MIDDLEWARE] configure_rate_limiting called")  # DEBUG
    # Добавляем limiter к app
    app.state.limiter = limiter

    # Добавляем обработчик ошибок rate limit
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    logger.info("Rate limiting configured successfully")
    logger.info(f"Default limit: {RATE_LIMITS['default']}")
    logger.info(f"API limit: {RATE_LIMITS['api']}")
    logger.info(f"Auth limit: {RATE_LIMITS['auth']}")
