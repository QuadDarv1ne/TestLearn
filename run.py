"""
Скрипт запуска приложения TestLearn.

Использование:
    python run.py              - Запуск с настройками по умолчанию
    python run.py --reload     - Запуск в режиме разработки с автоперезагрузкой
    python run.py --host 0.0.0.0 --port 8000  - Запуск на указанном хосте/порту

Для production рекомендуется использовать:
    uvicorn run:app --host 0.0.0.0 --port 8000 --workers 4
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# Загрузка переменных окружения перед импортом main
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def parse_args():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Запуск приложения TestLearn",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python run.py                      # Запуск на localhost:8000
  python run.py --reload             # Режим разработки с автоперезагрузкой
  python run.py --port 8080          # Запуск на порту 8080
  python run.py --host 0.0.0.0       # Запуск на всех интерфейсах
        """,
    )

    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("HOST", "0.0.0.0"),
        help="Хост для запуска (по умолчанию: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", 8000)),
        help="Порт для запуска (по умолчанию: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Режим разработки с автоперезагрузкой",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Количество workers (по умолчанию: 1)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default=os.getenv("LOG_LEVEL", "info"),
        choices=["debug", "info", "warning", "error", "critical"],
        help="Уровень логирования",
    )

    return parser.parse_args()


def main():
    """Точка входа приложения."""
    args = parse_args()

    # Импорт uvicorn здесь для избежания проблем с зависимостями
    try:
        import uvicorn
    except ImportError:
        logger.error("uvicorn не установлен. Установите: pip install uvicorn[standard]")
        sys.exit(1)

    logger.info(f"Запуск TestLearn на {args.host}:{args.port}")
    logger.info(f"Режим reload: {args.reload}")
    logger.info(f"Уровень логирования: {args.log_level}")

    # Конфигурация uvicorn
    config = {
        "app": "main:app",
        "host": args.host,
        "port": args.port,
        "reload": args.reload,
        "workers": args.workers if not args.reload else 1,
        "log_level": args.log_level,
    }

    # В режиме reload workers должен быть 1
    if args.reload:
        config["workers"] = 1
        logger.info("В режиме reload количество workers установлено в 1")

    logger.info(f"Документация API: http://{args.host}:{args.port}/api/docs")

    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
