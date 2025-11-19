"""
Лёгкий инструмент логирования.

• Файл журнала создаётся один раз при первом импорте модуля: logs/YYYYMMDD_HHMMSS.log
• Никаких env-параметров и чтения argv.
• Поддерживает:
    get_logger(name)          – любой произвольный логгер
    get_function_logger(func) – логгер функции/метода
    get_class_logger(obj)     – логгер экземпляра класса
"""

from __future__ import annotations

import contextvars
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from concurrent_log_handler import ConcurrentRotatingFileHandler

# ──────────────────────────────
# Параметры по умолчанию
# ──────────────────────────────
_LOG_DIR = Path("logs")
_LOG_DIR.mkdir(parents=True, exist_ok=True)

_LOG_FILE_NAME = "app.log"

_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
_LOG_FMT = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"

_current_name: contextvars.ContextVar[str] = contextvars.ContextVar(
    "current_name", default="default"
)

_cache: dict[str, logging.Logger] = {}  # кэш созданных логгеров


@lru_cache
def get_log_file(name: str) -> Path:
    return (_LOG_DIR / name).with_suffix(".log")


# ──────────────────────────────
# Внутренние функции
# ──────────────────────────────


def _build_logger(name: str, log_file_name: Optional[str]) -> logging.Logger:
    """Создаёт и настраивает новый logger с именем *name* (если его ещё нет)."""
    logger = logging.getLogger(name)
    log_file_name = log_file_name or _LOG_FILE_NAME
    log_file = get_log_file(log_file_name)

    # Если хендлеры уже установлены – значит логгер сконфигурирован; просто вернём его
    if logger.handlers:
        return logger

    logger.setLevel(_LOG_LEVEL)
    logger.propagate = False  # не дублируем записи в root-logger

    file_handler = ConcurrentRotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=7, encoding="utf-8"
    )
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter(_LOG_FMT)
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


# ──────────────────────────────
# Публичное API
# ──────────────────────────────


def get_logger(
    name: Optional[str] = None, *, log_file_name: Optional[str] = None
) -> logging.Logger:
    """
    Возвращает (и кеширует) логгер с указанным *name*.
    Если *name* не указан, используется текущее значение context-переменной «current_name».
    """
    name = name or _current_name.get()

    # Используем кэш, чтобы не создавать одинаковые логгеры
    if name not in _cache:
        _cache[name] = _build_logger(name, log_file_name)

    return _cache[name]


def get_function_logger(func, *, log_file_name: Optional[str] = None) -> logging.Logger:
    """Логгер вида «module:function»."""
    full_name = f"{func.__module__}:{func.__qualname__}"
    return get_logger(full_name, log_file_name=log_file_name)


def get_class_logger(obj, *, log_file_name: Optional[str] = None) -> logging.Logger:
    """Логгер вида «module:ClassName»."""
    full_name = f"{obj.__module__}:{obj.__class__.__qualname__}"
    return get_logger(full_name, log_file_name=log_file_name)


class ModulLogger:
    def __init__(self, log_file_name: str) -> None:
        self.log_file_name = log_file_name

    def get_logger(self, name: Optional[str] = None):
        return get_logger(name=name, log_file_name=self._log_file_name)

    def get_function_logger(self, func):
        return get_function_logger(func=func, log_file_name=self._log_file_name)

    def get_class_logger(self, obj):
        return get_class_logger(obj=obj, log_file_name=self.log_file_name)
