"""
Конфигурация логирования для приложения TestLearn.

Использование:
    from app.config.logging_config import setup_logging, get_logger
    
    logger = get_logger(__name__)
    logger.info("Сообщение")
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from typing import Optional


def get_log_level(level_name: str) -> int:
    """Получение уровня логирования из строки."""
    levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    return levels.get(level_name.upper(), logging.INFO)


def setup_logging(
    level: Optional[str] = None,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None,
    log_to_file: bool = False,
    log_file: Optional[str] = None,
    max_bytes: int = 10_000_000,
    backup_count: int = 5,
) -> logging.Logger:
    """
    Настройка логирования приложения.

    :param level: Уровень логирования (по умолчанию из LOG_LEVEL или INFO)
    :param log_format: Формат сообщений
    :param date_format: Формат даты
    :param log_to_file: Логировать в файл
    :param log_file: Путь к файлу логов
    :param max_bytes: Максимальный размер файла лога
    :param backup_count: Количество архивных файлов
    :return: Настроенный logger
    """
    # Конфигурация из env
    env_level = os.getenv("LOG_LEVEL", "INFO")
    env_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    env_date_format = "%Y-%m-%d %H:%M:%S"

    level = level or env_level
    log_format = log_format or env_format
    date_format = date_format or env_date_format

    # Получение корневого logger
    root_logger = logging.getLogger()
    root_logger.setLevel(get_log_level(level))

    # Очистка существующих handlers
    root_logger.handlers.clear()

    # Консольный handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(get_log_level(level))
    console_formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # Файловый handler (опционально)
    if log_to_file or os.getenv("LOG_TO_FILE", "false").lower() == "true":
        log_file_path = log_file or os.getenv("LOG_FILE", "logs/app.log")
        log_dir = Path(log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # Rotating file handler
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(get_log_level(level))
        file_formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt=date_format,
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Подавление лишних логов от библиотек
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("slowapi").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Получение logger по имени.

    :param name: Имя logger (обычно __name__)
    :return: Logger
    """
    return logging.getLogger(name)


# Глобальная настройка при имите
setup_logging()
